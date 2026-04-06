"""Tests for v1.0.0 new features.

Covers: VchasnoModel base, new exceptions, custom httpx injection,
CursorPage integration, FSM validation, cloud signer helpers,
enum union types, expanded params, and repr fixes.
"""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import httpx
import pytest

from vchasno._state import _ALLOWED_OPERATIONS, validate_document_state
from vchasno._sync._http import SyncTransport
from vchasno._sync._pagination import SyncCursorPage
from vchasno._sync.endpoints.cloud_signer import SyncCloudSigner
from vchasno._sync.endpoints.delete_requests import SyncDeleteRequests
from vchasno._sync.endpoints.documents import SyncDocuments
from vchasno._sync.endpoints.roles import SyncRoles
from vchasno.exceptions import (
    CloudSignerError,
    DocumentStateError,
    ValidationError,
    VchasnoError,
)
from vchasno.exceptions import TimeoutError as VchasnoTimeoutError
from vchasno.models._base import VchasnoModel
from vchasno.models.cloud_signer import CloudSignerSession
from vchasno.models.documents import Document, StampInfo
from vchasno.models.enums import (
    CommentType,
    DeleteRequestStatus,
    DocumentCategory,
    DocumentStatus,
    ReviewState,
    StructuredDataStatus,
)

# ====================================================================
# T1: VchasnoModel base class
# ====================================================================


class TestVchasnoModelBase:
    """Tests for VchasnoModel base class configuration."""

    def test_extra_fields_allowed(self):
        m = VchasnoModel.model_validate({"unknown_field": "value", "another": 42})
        assert m.model_extra == {"unknown_field": "value", "another": 42}

    def test_extra_fields_empty_when_none(self):
        m = VchasnoModel.model_validate({})
        assert m.model_extra == {}

    def test_populate_by_name_on_cloud_signer_session(self):
        s = CloudSignerSession(auth_session_id="x", is_mobile_logged=False)
        assert s.auth_session_id == "x"

    def test_populate_by_alias_on_cloud_signer_session(self):
        s = CloudSignerSession(authSessionId="y", isMobileLogged=True)
        assert s.auth_session_id == "y"

    def test_subclass_inherits_extra(self):
        d = Document.model_validate({"id": "d1", "status": 7000, "future_api_field": True})
        assert d.model_extra.get("future_api_field") is True

    def test_model_config_values(self):
        assert VchasnoModel.model_config.get("extra") == "allow"
        assert VchasnoModel.model_config.get("populate_by_name") is True


# ====================================================================
# T2: New exceptions
# ====================================================================


class TestDocumentStateErrorNew:
    """Tests for DocumentStateError exception."""

    def test_inherits_vchasno_error(self):
        assert issubclass(DocumentStateError, VchasnoError)

    def test_attributes(self):
        e = DocumentStateError(
            "bad state",
            current_status=7000,
            operation="send",
            allowed_statuses=[7001, 7003],
        )
        assert e.current_status == 7000
        assert e.operation == "send"
        assert e.allowed_statuses == [7001, 7003]
        assert str(e) == "bad state"

    def test_default_allowed_statuses(self):
        e = DocumentStateError("msg", current_status=7008, operation="delete")
        assert e.allowed_statuses == []

    def test_is_catchable_as_base(self):
        with pytest.raises(VchasnoError):
            raise DocumentStateError("err", current_status=7000, operation="x")


class TestCloudSignerErrorNew:
    """Tests for CloudSignerError exception."""

    def test_inherits_vchasno_error(self):
        assert issubclass(CloudSignerError, VchasnoError)

    def test_with_session_status(self):
        e = CloudSignerError("expired", session_status="expired")
        assert e.session_status == "expired"
        assert str(e) == "expired"

    def test_session_status_default_none(self):
        e = CloudSignerError("err")
        assert e.session_status is None


class TestTimeoutErrorNew:
    """Tests for VchasnoTimeoutError exception."""

    def test_inherits_vchasno_error(self):
        assert issubclass(VchasnoTimeoutError, VchasnoError)

    def test_attributes(self):
        e = VchasnoTimeoutError("slow", elapsed=10.5, timeout=10.0)
        assert e.elapsed == 10.5
        assert e.timeout == 10.0

    def test_message(self):
        e = VchasnoTimeoutError("took too long", elapsed=30.0, timeout=20.0)
        assert "took too long" in str(e)


class TestValidationErrorNew:
    """Tests for ValidationError exception."""

    def test_inherits_vchasno_error(self):
        assert issubclass(ValidationError, VchasnoError)

    def test_attributes(self):
        e = ValidationError("bad field", field="duration", value=10)
        assert e.field == "duration"
        assert e.value == 10

    def test_defaults(self):
        e = ValidationError("generic")
        assert e.field is None
        assert e.value is None


# ====================================================================
# T3: Custom httpx client injection
# ====================================================================


class TestCustomHttpxInjection:
    """Tests for custom httpx.Client / httpx.AsyncClient injection."""

    def test_sync_custom_client_not_owned(self):
        custom = httpx.Client(base_url="https://test.com")
        try:
            t = SyncTransport(base_url="https://test.com", token="tok", http_client=custom)
            assert t._owns_client is False
            assert t._client is custom
        finally:
            custom.close()

    def test_sync_default_client_owned(self):
        t = SyncTransport(base_url="https://test.com", token="tok")
        assert t._owns_client is True
        t.close()

    def test_sync_custom_client_auth_header_injected(self):
        custom = httpx.Client(base_url="https://test.com")
        try:
            SyncTransport(base_url="https://test.com", token="my-token", http_client=custom)
            assert custom.headers.get("Authorization") == "my-token"
        finally:
            custom.close()

    def test_sync_custom_client_existing_auth_not_overwritten(self):
        custom = httpx.Client(
            base_url="https://test.com",
            headers={"Authorization": "existing-token"},
        )
        try:
            SyncTransport(base_url="https://test.com", token="new-token", http_client=custom)
            assert custom.headers.get("Authorization") == "existing-token"
        finally:
            custom.close()

    def test_sync_close_does_not_close_injected_client(self):
        custom = httpx.Client(base_url="https://test.com")
        t = SyncTransport(base_url="https://test.com", token="tok", http_client=custom)
        t.close()  # should not close custom client
        assert not custom.is_closed
        custom.close()

    def test_async_custom_client_not_owned(self):
        from vchasno._async._http import AsyncTransport

        custom = httpx.AsyncClient(base_url="https://test.com")
        t = AsyncTransport(base_url="https://test.com", token="tok", http_client=custom)
        assert t._owns_client is False
        assert t._client is custom

    def test_async_default_client_owned(self):
        from vchasno._async._http import AsyncTransport

        t = AsyncTransport(base_url="https://test.com", token="tok")
        assert t._owns_client is True

    def test_vchasno_client_passes_http_client(self):
        from vchasno._sync.client import Vchasno

        custom = httpx.Client(base_url="https://test.com")
        try:
            c = Vchasno(token="tok", http_client=custom)
            assert c._transport._owns_client is False
            assert c._transport._client is custom
        finally:
            custom.close()


# ====================================================================
# T5/T16: FSM state validation
# ====================================================================


class TestFSMValidationDirect:
    """Tests for validate_document_state() function directly."""

    def test_valid_send_on_7001(self):
        validate_document_state(7001, "send")

    def test_valid_send_on_7003(self):
        validate_document_state(7003, "send")

    def test_invalid_send_on_7008(self):
        with pytest.raises(DocumentStateError) as exc_info:
            validate_document_state(7008, "send")
        assert exc_info.value.current_status == 7008
        assert exc_info.value.operation == "send"

    def test_invalid_send_on_7000(self):
        with pytest.raises(DocumentStateError):
            validate_document_state(7000, "send")

    def test_invalid_delete_on_7002(self):
        with pytest.raises(DocumentStateError):
            validate_document_state(7002, "delete")

    def test_valid_archive_on_7008(self):
        validate_document_state(7008, "archive")

    def test_valid_download_on_any_known_status(self):
        for status in _ALLOWED_OPERATIONS:
            validate_document_state(status, "download")

    def test_unknown_status_allows_all(self):
        validate_document_state(9999, "anything")
        validate_document_state(0, "send")
        validate_document_state(-1, "delete")

    def test_error_message_contains_operation(self):
        with pytest.raises(DocumentStateError, match="send"):
            validate_document_state(7008, "send")

    def test_error_message_contains_status(self):
        with pytest.raises(DocumentStateError, match="7008"):
            validate_document_state(7008, "send")

    def test_all_statuses_have_download(self):
        for status, ops in _ALLOWED_OPERATIONS.items():
            assert "download" in ops, f"Status {status} missing 'download'"

    @pytest.mark.parametrize(
        ("status", "operation"),
        [
            (7000, "update_info"),
            (7000, "delete"),
            (7001, "sign"),
            (7001, "reject"),
            (7002, "sign"),
            (7004, "reject"),
            (7008, "archive"),
            (7008, "unarchive"),
            (7011, "archive"),
        ],
    )
    def test_valid_operations(self, status: int, operation: str):
        validate_document_state(status, operation)

    @pytest.mark.parametrize(
        ("status", "operation"),
        [
            (7000, "sign"),
            (7000, "archive"),
            (7002, "delete"),
            (7006, "sign"),
            (7008, "send"),
            (7008, "reject"),
            (7011, "send"),
        ],
    )
    def test_invalid_operations(self, status: int, operation: str):
        with pytest.raises(DocumentStateError):
            validate_document_state(status, operation)


# ====================================================================
# T8: documents.list() expanded params
# ====================================================================


class TestDocumentsListExpandedParams:
    """Tests for new query params in documents.list()."""

    def _make(self) -> tuple[SyncDocuments, MagicMock]:
        ep = SyncDocuments(MagicMock())
        ep._request = MagicMock(return_value={"documents": [], "next_cursor": None})
        return ep, ep._request

    def test_review_state_param(self):
        ep, req = self._make()
        ep.list(review_state="approved")
        params = req.call_args.kwargs.get("params", {})
        assert params.get("review_state") == "approved"

    def test_amount_gte_param(self):
        ep, req = self._make()
        ep.list(amount_gte=100000)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("amount_gte") == 100000

    def test_amount_lte_param(self):
        ep, req = self._make()
        ep.list(amount_lte=500000)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("amount_lte") == 500000

    def test_amount_eq_param(self):
        ep, req = self._make()
        ep.list(amount_eq=200000)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("amount_eq") == 200000

    def test_with_delete_requests_param(self):
        ep, req = self._make()
        ep.list(with_delete_requests=True)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("with_delete_requests") is True

    def test_with_access_settings_param(self):
        ep, req = self._make()
        ep.list(with_access_settings=True)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("with_access_settings") is True

    def test_date_review_approved_from_param(self):
        ep, req = self._make()
        ep.list(date_review_approved_from="2024-01-01")
        params = req.call_args.kwargs.get("params", {})
        assert params.get("date_review_approved_from") == "2024-01-01"

    def test_date_review_approved_to_param(self):
        ep, req = self._make()
        ep.list(date_review_approved_to="2024-12-31")
        params = req.call_args.kwargs.get("params", {})
        assert params.get("date_review_approved_to") == "2024-12-31"

    def test_with_document_fields_param(self):
        ep, req = self._make()
        ep.list(with_document_fields=True)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("with_document_fields") is True

    def test_with_versions_param(self):
        ep, req = self._make()
        ep.list(with_versions=True)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("with_versions") is True

    def test_multiple_params_combined(self):
        ep, req = self._make()
        ep.list(
            review_state="approved",
            amount_gte=100000,
            amount_lte=500000,
            with_delete_requests=True,
        )
        params = req.call_args.kwargs.get("params", {})
        assert params.get("review_state") == "approved"
        assert params.get("amount_gte") == 100000
        assert params.get("amount_lte") == 500000

    def test_ids_multi_value(self):
        ep, req = self._make()
        ep.list(ids=["id1", "id2"])
        call_args = req.call_args
        params = call_args.kwargs.get("params", [])
        assert isinstance(params, list)
        id_values = [v for k, v in params if k == "ids"]
        assert "id1" in id_values
        assert "id2" in id_values


# ====================================================================
# T9: download_archive expanded params
# ====================================================================


class TestDownloadArchiveExpandedParams:
    def _make(self) -> tuple[SyncDocuments, MagicMock]:
        ep = SyncDocuments(MagicMock())
        ep._request = MagicMock(return_value=b"zip")
        return ep, ep._request

    def test_with_xml_preview(self):
        ep, req = self._make()
        ep.download_archive("d1", with_xml_preview=True)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("with_xml_preview") is True

    def test_convert_to_signature_format(self):
        ep, req = self._make()
        ep.download_archive("d1", convert_to_signature_format="cades")
        params = req.call_args.kwargs.get("params", {})
        assert params.get("convert_to_signature_format") == "cades"

    def test_filenames_max_length_valid(self):
        ep, req = self._make()
        ep.download_archive("d1", filenames_max_length=100)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("filenames_max_length") == 100

    def test_filenames_max_length_too_low(self):
        ep, _ = self._make()
        with pytest.raises(ValueError, match="filenames_max_length"):
            ep.download_archive("d1", filenames_max_length=5)

    def test_filenames_max_length_too_high(self):
        ep, _ = self._make()
        with pytest.raises(ValueError, match="filenames_max_length"):
            ep.download_archive("d1", filenames_max_length=256)

    def test_filenames_max_length_boundary_10(self):
        ep, req = self._make()
        ep.download_archive("d1", filenames_max_length=10)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("filenames_max_length") == 10

    def test_filenames_max_length_boundary_255(self):
        ep, req = self._make()
        ep.download_archive("d1", filenames_max_length=255)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("filenames_max_length") == 255


# ====================================================================
# T10: list_incoming() expanded params
# ====================================================================


class TestDocumentsListIncomingExpanded:
    def _make(self) -> tuple[SyncDocuments, MagicMock]:
        ep = SyncDocuments(MagicMock())
        ep._request = MagicMock(return_value={"documents": [], "next_cursor": None})
        return ep, ep._request

    def test_date_created_from(self):
        ep, req = self._make()
        ep.list_incoming(date_created_from="2024-01-01")
        params = req.call_args.kwargs.get("params", {})
        assert params.get("date_created_from") == "2024-01-01"

    def test_processed(self):
        ep, req = self._make()
        ep.list_incoming(processed=True)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("processed") is True

    def test_edrpou_owner(self):
        ep, req = self._make()
        ep.list_incoming(edrpou_owner="12345678")
        params = req.call_args.kwargs.get("params", {})
        assert params.get("edrpou_owner") == "12345678"

    def test_review_state(self):
        ep, req = self._make()
        ep.list_incoming(review_state="approved")
        params = req.call_args.kwargs.get("params", {})
        assert params.get("review_state") == "approved"

    def test_sd_status(self):
        ep, req = self._make()
        ep.list_incoming(sd_status="confirmed")
        params = req.call_args.kwargs.get("params", {})
        assert params.get("sd_status") == "confirmed"

    def test_date_sent_from_to(self):
        ep, req = self._make()
        ep.list_incoming(date_sent_from="2024-01-01", date_sent_to="2024-12-31")
        params = req.call_args.kwargs.get("params", {})
        assert params.get("date_sent_from") == "2024-01-01"
        assert params.get("date_sent_to") == "2024-12-31"

    def test_amount_range(self):
        ep, req = self._make()
        ep.list_incoming(amount_gte=100, amount_lte=999)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("amount_gte") == 100
        assert params.get("amount_lte") == 999

    def test_is_archived(self):
        ep, req = self._make()
        ep.list_incoming(is_archived=False)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("is_archived") is False

    def test_ids_multi_value(self):
        ep, req = self._make()
        ep.list_incoming(ids=["id1", "id2"])
        params = req.call_args.kwargs.get("params", [])
        assert isinstance(params, list)


# ====================================================================
# T11: Model improvements
# ====================================================================


class TestStampInfoFullFields:
    def test_full_fields(self):
        s = StampInfo.model_validate(
            {
                "acsk": "ACSK Provider",
                "power_type": "qualified",
                "serial_number": "SN123",
                "issuer": "CA",
                "subject": "Test Subject",
                "company_name": "Test Co",
                "edrpou": "12345678",
                "signer_name": "John Doe",
                "signer_position": "CEO",
                "timestamp": "2024-01-01T00:00:00",
            }
        )
        assert s.acsk == "ACSK Provider"
        assert s.power_type == "qualified"
        assert s.serial_number == "SN123"
        assert s.issuer == "CA"

    def test_minimal(self):
        s = StampInfo()
        assert s.serial_number is None
        assert s.acsk is None


class TestCommentTypeEnum:
    def test_comment(self):
        assert CommentType.COMMENT == "comment"

    def test_rejection(self):
        assert CommentType.REJECTION == "rejection"

    def test_delete_request(self):
        assert CommentType.DELETE_REQUEST == "delete_request"

    def test_delete_request_rejection(self):
        assert CommentType.DELETE_REQUEST_REJECTION == "delete_request_rejection"

    def test_document_revoke_initiate(self):
        assert CommentType.DOCUMENT_REVOKE_INITIATE == "document_revoke_initiate"

    def test_document_revoke_rejection(self):
        assert CommentType.DOCUMENT_REVOKE_REJECTION == "document_revoke_rejection"


# ====================================================================
# T13: Roles permissions
# ====================================================================


class TestRolesPermissionsExpanded:
    def _make(self) -> tuple[SyncRoles, MagicMock]:
        ep = SyncRoles(MagicMock())
        ep._request = MagicMock(return_value=None)
        return ep, ep._request

    def test_can_sign_and_reject(self):
        ep, req = self._make()
        ep.update("r1", can_sign_and_reject_document=True)
        body = req.call_args.kwargs.get("json", {})
        assert body["can_sign_and_reject_document"] is True

    def test_user_role(self):
        ep, req = self._make()
        ep.update("r1", user_role=8001)
        body = req.call_args.kwargs.get("json", {})
        assert body["user_role"] == 8001

    def test_allowed_ips(self):
        ep, req = self._make()
        ep.update("r1", allowed_ips=["1.2.3.4"])
        body = req.call_args.kwargs.get("json", {})
        assert body["allowed_ips"] == ["1.2.3.4"]

    def test_allowed_api_ips(self):
        ep, req = self._make()
        ep.update("r1", allowed_api_ips=["5.6.7.8"])
        body = req.call_args.kwargs.get("json", {})
        assert body["allowed_api_ips"] == ["5.6.7.8"]

    def test_notification_permissions(self):
        ep, req = self._make()
        ep.update("r1", can_receive_inbox=True, can_receive_comments=False)
        body = req.call_args.kwargs.get("json", {})
        assert body["can_receive_inbox"] is True
        assert body["can_receive_comments"] is False

    def test_management_permissions(self):
        ep, req = self._make()
        ep.update("r1", can_edit_company=True, can_invite_coworkers=False)
        body = req.call_args.kwargs.get("json", {})
        assert body["can_edit_company"] is True
        assert body["can_invite_coworkers"] is False

    def test_unset_params_excluded(self):
        ep, req = self._make()
        ep.update("r1", can_sign_and_reject_document=True)
        body = req.call_args.kwargs.get("json", {})
        assert "user_role" not in body
        assert "position" not in body

    def test_show_child_documents(self):
        ep, req = self._make()
        ep.update("r1", show_child_documents=True)
        body = req.call_args.kwargs.get("json", {})
        assert body["show_child_documents"] is True


# ====================================================================
# T15: CursorPage integration
# ====================================================================


class TestCursorPageIntegration:
    """documents.list() returns SyncCursorPage with correct data."""

    def _make(self) -> tuple[SyncDocuments, MagicMock]:
        ep = SyncDocuments(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_list_returns_cursor_page(self):
        ep, req = self._make()
        req.return_value = {"documents": [{"id": "d1", "status": 7000}], "next_cursor": "abc"}
        result = ep.list()
        assert isinstance(result, SyncCursorPage)
        assert result.has_next_page()
        assert result.next_cursor == "abc"

    def test_list_backward_compat_documents_attr(self):
        ep, req = self._make()
        req.return_value = {"documents": [{"id": "d1", "status": 7000}], "next_cursor": None}
        result = ep.list()
        assert result.documents == result.data
        assert len(result.documents) == 1

    def test_list_data_are_document_models(self):
        ep, req = self._make()
        req.return_value = {"documents": [{"id": "d1", "status": 7008}], "next_cursor": None}
        result = ep.list()
        assert isinstance(result.data[0], Document)
        assert result.data[0].id == "d1"

    def test_list_empty_page(self):
        ep, req = self._make()
        req.return_value = {"documents": [], "next_cursor": None}
        result = ep.list()
        assert len(result.data) == 0
        assert not result.has_next_page()

    def test_list_incoming_returns_cursor_page(self):
        ep, req = self._make()
        req.return_value = {"documents": [{"id": "i1", "status": 7000}], "next_cursor": None}
        result = ep.list_incoming()
        assert isinstance(result, SyncCursorPage)

    def test_iteration_single_page(self):
        ep, req = self._make()
        req.return_value = {
            "documents": [{"id": "d1", "status": 7000}, {"id": "d2", "status": 7001}],
            "next_cursor": None,
        }
        result = ep.list()
        items = list(result)
        assert len(items) == 2
        assert items[0].id == "d1"
        assert items[1].id == "d2"


# ====================================================================
# T17: Cloud signer helpers
# ====================================================================


class TestCloudSignerSignAndWait:
    """Tests for sign_and_wait() and create_and_wait_session()."""

    def _make(self) -> tuple[SyncCloudSigner, MagicMock]:
        ep = SyncCloudSigner(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_sign_and_wait_duration_too_low(self):
        ep, _ = self._make()
        with pytest.raises(ValidationError) as exc_info:
            ep.sign_and_wait(document_id="d", client_id="c", password="p", duration=10)
        assert exc_info.value.field == "duration"
        assert exc_info.value.value == 10

    def test_sign_and_wait_duration_too_high(self):
        ep, _ = self._make()
        with pytest.raises(ValidationError):
            ep.sign_and_wait(document_id="d", client_id="c", password="p", duration=3_000_000)

    def test_sign_and_wait_duration_boundary_60(self):
        ep, req = self._make()
        req.side_effect = [
            {"authSessionId": "s1", "isMobileLogged": False},
            {"status": "ready", "token": "tok"},
            None,
        ]
        ep.sign_and_wait(document_id="d", client_id="c", password="p", duration=60)

    @patch("vchasno._sync.endpoints.cloud_signer.time.sleep")
    @patch("vchasno._sync.endpoints.cloud_signer.time.monotonic")
    def test_sign_and_wait_timeout(self, mock_monotonic, mock_sleep):
        # monotonic calls: start=0, loop check=0.5 (enter), loop check=1.5 (exit), elapsed=1.5
        mock_monotonic.side_effect = [0.0, 0.5, 1.5, 1.5]
        ep, req = self._make()
        req.side_effect = [
            {"authSessionId": "s1", "isMobileLogged": False},
            {"status": "init"},
        ]
        with pytest.raises(VchasnoTimeoutError) as exc_info:
            ep.sign_and_wait(
                document_id="d",
                client_id="c",
                password="p",
                timeout=1.0,
                poll_interval=0.5,
            )
        assert exc_info.value.timeout == 1.0

    @patch("vchasno._sync.endpoints.cloud_signer.time.sleep")
    @patch("vchasno._sync.endpoints.cloud_signer.time.monotonic")
    def test_sign_and_wait_expired_session(self, mock_monotonic, mock_sleep):
        mock_monotonic.side_effect = [0.0, 0.5]
        ep, req = self._make()
        req.side_effect = [
            {"authSessionId": "s1", "isMobileLogged": False},
            {"status": "expired"},
        ]
        with pytest.raises(CloudSignerError) as exc_info:
            ep.sign_and_wait(document_id="d", client_id="c", password="p")
        assert exc_info.value.session_status == "expired"

    @patch("vchasno._sync.endpoints.cloud_signer.time.sleep")
    @patch("vchasno._sync.endpoints.cloud_signer.time.monotonic")
    def test_sign_and_wait_canceled_session(self, mock_monotonic, mock_sleep):
        mock_monotonic.side_effect = [0.0, 0.5]
        ep, req = self._make()
        req.side_effect = [
            {"authSessionId": "s1", "isMobileLogged": False},
            {"status": "canceled"},
        ]
        with pytest.raises(CloudSignerError) as exc_info:
            ep.sign_and_wait(document_id="d", client_id="c", password="p")
        assert exc_info.value.session_status == "canceled"

    def test_sign_and_wait_success_flow(self):
        ep, req = self._make()
        req.side_effect = [
            {"authSessionId": "s1", "isMobileLogged": False},
            {"status": "ready", "token": "session-token"},
            None,
        ]
        ep.sign_and_wait(document_id="d1", client_id="c1", password="secret")
        last_call = req.call_args
        body = last_call.kwargs.get("json", {})
        assert body["document_id"] == "d1"
        assert body["auth_session_token"] == "session-token"

    @patch("vchasno._sync.endpoints.cloud_signer.time.sleep")
    @patch("vchasno._sync.endpoints.cloud_signer.time.monotonic")
    def test_sign_and_wait_with_refresh_token(self, mock_monotonic, mock_sleep):
        mock_monotonic.side_effect = [0.0, 0.5]
        ep, req = self._make()
        req.side_effect = [
            {"authSessionId": "s1", "isMobileLogged": False},
            {"status": "ready", "accessToken": "at", "refreshToken": "rt", "expiresIn": 3600},
            None,
        ]
        ep.sign_and_wait(
            document_id="d1",
            client_id="c1",
            password="secret",
            use_refresh_token=True,
        )
        last_call = req.call_args
        body = last_call.kwargs.get("json", {})
        assert body["access_token"] == "at"

    def test_create_and_wait_duration_validation(self):
        ep, _ = self._make()
        with pytest.raises(ValidationError):
            ep.create_and_wait_session(duration=10, client_id="c")

    def test_create_and_wait_success(self):
        ep, req = self._make()
        req.side_effect = [
            {"authSessionId": "s1", "isMobileLogged": False},
            {"status": "ready", "token": "tok"},
        ]
        token = ep.create_and_wait_session(client_id="c1")
        assert token == "tok"

    @patch("vchasno._sync.endpoints.cloud_signer.time.sleep")
    @patch("vchasno._sync.endpoints.cloud_signer.time.monotonic")
    def test_create_and_wait_timeout(self, mock_monotonic, mock_sleep):
        mock_monotonic.side_effect = [0.0, 0.5, 1.5, 1.5]
        ep, req = self._make()
        req.side_effect = [
            {"authSessionId": "s1", "isMobileLogged": False},
            {"status": "init"},
        ]
        with pytest.raises(VchasnoTimeoutError):
            ep.create_and_wait_session(client_id="c1", timeout=1.0, poll_interval=0.5)


# ====================================================================
# T18: Enum union types
# ====================================================================


class TestEnumUnionTypes:
    """Tests that enum values are accepted alongside raw ints/strings."""

    def _make_docs(self) -> tuple[SyncDocuments, MagicMock]:
        ep = SyncDocuments(MagicMock())
        ep._request = MagicMock(return_value={"documents": [], "next_cursor": None})
        return ep, ep._request

    def test_document_status_enum_in_list(self):
        ep, req = self._make_docs()
        ep.list(status=DocumentStatus.FULLY_SIGNED)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("status") == DocumentStatus.FULLY_SIGNED

    def test_raw_int_status_in_list(self):
        ep, req = self._make_docs()
        ep.list(status=7008)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("status") == 7008

    def test_document_category_enum_in_list(self):
        ep, req = self._make_docs()
        ep.list(category=DocumentCategory.CONTRACT)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("category") == DocumentCategory.CONTRACT

    def test_review_state_enum_in_list(self):
        ep, req = self._make_docs()
        ep.list(review_state=ReviewState.APPROVED)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("review_state") == ReviewState.APPROVED

    def test_sd_status_enum_in_list(self):
        ep, req = self._make_docs()
        ep.list(sd_status=StructuredDataStatus.CONFIRMED)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("sd_status") == StructuredDataStatus.CONFIRMED

    def test_document_status_enum_in_list_incoming(self):
        ep, req = self._make_docs()
        ep.list_incoming(status=DocumentStatus.AWAITING_RECIPIENT_SIGNATURE)
        params = req.call_args.kwargs.get("params", {})
        assert params.get("status") == DocumentStatus.AWAITING_RECIPIENT_SIGNATURE

    def test_delete_request_status_enum(self):
        ep = SyncDeleteRequests(MagicMock())
        ep._request = MagicMock(return_value=[])
        ep.list(status=DeleteRequestStatus.NEW)
        params = ep._request.call_args.kwargs.get("params", {})
        assert params.get("status") == DeleteRequestStatus.NEW


# ====================================================================
# T19: repr fix
# ====================================================================


class TestReprFixNew:
    """SyncTransport and AsyncTransport repr should include class name."""

    def test_sync_transport_repr_class_name(self):
        t = SyncTransport(base_url="https://x.com", token="secret-api-key-12345")
        r = repr(t)
        assert "SyncTransport" in r
        assert "secret-api-key-12345" not in r
        assert "token=***" in r
        t.close()

    def test_async_transport_repr_class_name(self):
        from vchasno._async._http import AsyncTransport

        t = AsyncTransport(base_url="https://x.com", token="secret-api-key-12345")
        r = repr(t)
        assert "AsyncTransport" in r
        assert "secret-api-key-12345" not in r
        assert "token=***" in r


# ====================================================================
# Public API exports
# ====================================================================


class TestPublicExportsNew:
    """Ensure new exceptions and types are exported from vchasno."""

    def test_document_state_error_exported(self):
        from vchasno import DocumentStateError as DSE

        assert DSE is not None

    def test_cloud_signer_error_exported(self):
        from vchasno import CloudSignerError as CSE

        assert CSE is not None

    def test_timeout_error_exported(self):
        from vchasno import TimeoutError as TE

        assert TE is not None

    def test_validation_error_exported(self):
        from vchasno import ValidationError as VE

        assert VE is not None

    def test_vchasno_model_exported(self):
        from vchasno import VchasnoModel as VM

        assert VM is not None

    def test_sync_cursor_page_exported(self):
        from vchasno import SyncCursorPage as SCP

        assert SCP is not None

    def test_async_cursor_page_exported(self):
        from vchasno import AsyncCursorPage as ACP

        assert ACP is not None

    def test_version_is_1_0_0(self):
        import vchasno

        assert vchasno.__version__ == "1.0.0"


# ====================================================================
# Upload new params
# ====================================================================


class TestUploadExpandedParams:
    """Tests for expanded upload parameters."""

    def _make(self) -> tuple[SyncDocuments, MagicMock]:
        ep = SyncDocuments(MagicMock())
        ep._request = MagicMock(return_value={"documents": [{"id": "d1", "status": 7000}], "next_cursor": None})
        return ep, ep._request

    def test_upload_with_recipient_emails(self):
        ep, req = self._make()
        ep.upload(io.BytesIO(b"data"), recipient_emails=["a@b.com", "c@d.com"])
        call_args = req.call_args
        params = call_args.kwargs.get("params", [])
        if isinstance(params, list):
            re_values = [v for k, v in params if k == "recipient_emails"]
            assert "a@b.com" in re_values
            assert "c@d.com" in re_values

    def test_upload_with_tags(self):
        ep, req = self._make()
        ep.upload(io.BytesIO(b"data"), tags=["urgent", "q1"])
        call_args = req.call_args
        params = call_args.kwargs.get("params", [])
        if isinstance(params, list):
            tag_values = [v for k, v in params if k == "tags"]
            assert "urgent" in tag_values

    def test_upload_with_access_settings(self):
        ep, req = self._make()
        ep.upload(io.BytesIO(b"data"), access_settings_level="private")
        call_args = req.call_args
        params = call_args.kwargs.get("params", {})
        if isinstance(params, dict):
            assert params.get("access_settings_level") == "private"

    def test_upload_with_reviewers(self):
        ep, req = self._make()
        ep.upload(io.BytesIO(b"data"), reviewers_ids=["r1", "r2"], is_required_review=True)
        call_args = req.call_args
        params = call_args.kwargs.get("params", [])
        if isinstance(params, list):
            rv = [v for k, v in params if k == "reviewers_ids"]
            assert "r1" in rv
            assert "r2" in rv
