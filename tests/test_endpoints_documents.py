"""Tests for vchasno.endpoints.documents."""

from __future__ import annotations

import io
import tempfile
from unittest.mock import AsyncMock, MagicMock

import pytest

from vchasno._async._pagination import AsyncCursorPage
from vchasno._async.endpoints.documents import AsyncDocuments
from vchasno._sync._pagination import SyncCursorPage
from vchasno._sync.endpoints.documents import SyncDocuments
from vchasno.exceptions import DocumentStateError
from vchasno.models.common import UpdatedIds
from vchasno.models.documents import (
    Document,
    DocumentList,
    DocumentStatusList,
    DownloadDocumentList,
)

DOC_DATA = {"id": "d1", "status": 7000}
DOC_LIST_DATA = {"documents": [DOC_DATA], "next_cursor": None}
INCOMING_DOC_DATA = {"id": "i1", "status": 7000}
INCOMING_DOC_LIST_DATA = {"documents": [INCOMING_DOC_DATA], "next_cursor": None}


class TestSyncDocuments:
    def _make(self) -> tuple[SyncDocuments, MagicMock]:
        transport = MagicMock()
        ep = SyncDocuments(transport)
        ep._request = MagicMock()
        return ep, ep._request

    def test_list(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        result = ep.list(status=7000)
        assert isinstance(result, SyncCursorPage)
        assert len(result.data) == 1
        assert result.documents == result.data
        req.assert_called_once_with("GET", "/api/v2/documents", params={"status": 7000})

    def test_list_no_params(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        ep.list()
        req.assert_called_once_with("GET", "/api/v2/documents", params=None)

    def test_get_wrapped(self):
        ep, req = self._make()
        req.return_value = {"documents": [DOC_DATA]}
        result = ep.get("d1")
        assert isinstance(result, Document)
        assert result.id == "d1"

    def test_get_unwrapped(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        result = ep.get("d1")
        assert isinstance(result, Document)

    def test_upload_with_binary_io(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        buf = io.BytesIO(b"content")
        result = ep.upload(buf)
        assert isinstance(result, DocumentList)

    def test_upload_with_binary_io_default_filename(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        buf = io.BytesIO(b"content")
        ep.upload(buf)
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files") or call_kwargs[1].get("files")
        assert files_arg[0][1][0] == "document"

    def test_upload_with_path(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"data")
            f.flush()
            result = ep.upload(f.name)
        assert isinstance(result, DocumentList)

    def test_upload_unwrapped_response(self):
        ep, req = self._make()
        req.return_value = DOC_DATA  # not wrapped
        buf = io.BytesIO(b"content")
        result = ep.upload(buf)
        assert isinstance(result, DocumentList)
        assert len(result.documents) == 1

    def test_upload_with_custom_filename(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        buf = io.BytesIO(b"content")
        ep.upload(buf, filename="custom.pdf")
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files") or call_kwargs[1].get("files")
        assert files_arg[0][1][0] == "custom.pdf"

    def test_update_info(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        result = ep.update_info("d1", title="New Title", validate=False)
        assert isinstance(result, Document)

    def test_update_recipient(self):
        ep, req = self._make()
        req.return_value = None
        ep.update_recipient("d1", edrpou="12345678", email="e@m.com", validate=False)
        req.assert_called_once()

    def test_update_access_settings(self):
        ep, req = self._make()
        req.return_value = None
        ep.update_access_settings("d1", level="private")
        req.assert_called_once()

    def test_update_viewers_with_groups_and_roles(self):
        ep, req = self._make()
        req.return_value = None
        ep.update_viewers("d1", strategy="add", groups_ids=["g1"], roles_ids=["r1"])
        call_json = req.call_args.kwargs["json"]
        assert call_json["groups_ids"] == ["g1"]
        assert call_json["roles_ids"] == ["r1"]

    def test_update_viewers_without_optional(self):
        ep, req = self._make()
        req.return_value = None
        ep.update_viewers("d1", strategy="replace")
        call_json = req.call_args.kwargs["json"]
        assert "groups_ids" not in call_json
        assert "roles_ids" not in call_json

    def test_set_flow(self):
        ep, req = self._make()
        req.return_value = None
        ep.set_flow("d1", [{"edrpou": "e", "order": 1}], validate=False)
        req.assert_called_once()
        assert req.call_args.kwargs["json"] == [{"edrpou": "e", "order": 1}]

    def test_list_incoming(self):
        ep, req = self._make()
        req.return_value = INCOMING_DOC_LIST_DATA
        result = ep.list_incoming(status=7000)
        assert isinstance(result, SyncCursorPage)
        assert len(result.data) == 1
        assert result.documents == result.data

    def test_set_signers(self):
        ep, req = self._make()
        req.return_value = None
        ep.set_signers("d1", signer_entities=[{"email": "e@m.com"}], is_parallel=False, validate=False)
        req.assert_called_once()

    def test_download_original_no_version(self):
        ep, req = self._make()
        req.return_value = b"bytes"
        result = ep.download_original("d1")
        assert result == b"bytes"
        req.assert_called_with("GET", "/api/v2/documents/d1/original", params=None)

    def test_download_original_with_version(self):
        ep, req = self._make()
        req.return_value = b"bytes"
        ep.download_original("d1", version="v1")
        req.assert_called_with("GET", "/api/v2/documents/d1/original", params={"version": "v1"})

    def test_download_archive(self):
        ep, req = self._make()
        req.return_value = b"zip"
        result = ep.download_archive("d1")
        assert result == b"zip"

    def test_download_p7s(self):
        ep, req = self._make()
        req.return_value = b"p7s"
        assert ep.download_p7s("d1") == b"p7s"

    def test_download_asic(self):
        ep, req = self._make()
        req.return_value = b"asic"
        assert ep.download_asic("d1") == b"asic"

    def test_download_documents(self):
        ep, req = self._make()
        req.return_value = {"documents": [{"id": "d1"}], "status": 200, "ready": True, "pending": False, "total": 1}
        result = ep.download_documents(["d1"])
        assert isinstance(result, DownloadDocumentList)

    def test_xml_to_pdf_create(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.xml_to_pdf_create("d1", force=True)
        req.assert_called_with("POST", "/api/v2/documents/d1/xml-to-pdf", json={"force": True})

    def test_xml_to_pdf_download(self):
        ep, req = self._make()
        req.return_value = b"pdf"
        assert ep.xml_to_pdf_download("d1") == b"pdf"

    def test_pdf_print(self):
        ep, req = self._make()
        req.return_value = b"pdf"
        assert ep.pdf_print("d1") == b"pdf"

    def test_statuses(self):
        ep, req = self._make()
        req.return_value = {"data_list": [{"document_id": "d1", "status_id": 7000, "status_text": "Uploaded"}]}
        result = ep.statuses(["d1"])
        assert isinstance(result, DocumentStatusList)

    def test_reject(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.reject("d1", text="reason", validate=False)
        req.assert_called_with("POST", "/api/v2/documents/d1/reject", json={"text": "reason"})

    def test_send(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.send("d1", validate=False)
        req.assert_called_with("POST", "/api/v2/documents/d1/send")

    def test_delete(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.delete("d1", validate=False)
        req.assert_called_with("DELETE", "/api/v2/documents/d1")

    def test_archive_with_directory(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.archive(["d1"], directory_id="dir1")
        req.assert_called_with(
            "POST", "/api/v2/documents/archive", json={"document_ids": ["d1"], "directory_id": "dir1"}
        )

    def test_archive_without_directory(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.archive(["d1"])
        call_json = req.call_args.kwargs["json"]
        assert "directory_id" not in call_json

    def test_unarchive(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.unarchive(["d1"])
        req.assert_called_with("DELETE", "/api/v2/documents/archive", json={"document_ids": ["d1"]})

    def test_mark_as_processed(self):
        ep, req = self._make()
        req.return_value = {"updated_ids": ["d1"]}
        result = ep.mark_as_processed(["d1"])
        assert isinstance(result, UpdatedIds)

    def test_structured_data_download(self):
        ep, req = self._make()
        req.return_value = {"details": {}}
        ep.structured_data_download("d1", output_format="json")
        req.assert_called_with("GET", "/api/v2/documents/d1/structured-data/download", params={"format": "json"})

    def test_download_archive_with_instruction(self):
        ep, req = self._make()
        req.return_value = b"zip-data"
        ep.download_archive("d1", with_instruction=1)
        assert req.call_args.kwargs["params"] == {"with_instruction": 1}

    def test_statuses_rejects_over_500(self):
        ep, _ = self._make()
        with pytest.raises(ValueError, match="500"):
            ep.statuses(["id"] * 501)

    def test_upload_recipient_edrpou(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"test")
            f.flush()
            path = f.name
        try:
            ep.upload(path, recipient_edrpou="12345678")
            # recipient_edrpou is resolved to 'edrpou' query param by collect_params
            call_params = req.call_args.kwargs.get("params", {})
            assert call_params.get("edrpou") == "12345678"
        finally:
            import os

            os.unlink(path)


class TestAsyncDocuments:
    def _make(self) -> tuple[AsyncDocuments, AsyncMock]:
        transport = MagicMock()
        ep = AsyncDocuments(transport)
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_list(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        result = await ep.list(status=7000)
        assert isinstance(result, AsyncCursorPage)
        assert len(result.data) == 1
        assert result.documents == result.data

    @pytest.mark.asyncio
    async def test_list_no_params(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        await ep.list()
        req.assert_called_once_with("GET", "/api/v2/documents", params=None)

    @pytest.mark.asyncio
    async def test_get_wrapped(self):
        ep, req = self._make()
        req.return_value = {"documents": [DOC_DATA]}
        result = await ep.get("d1")
        assert isinstance(result, Document)

    @pytest.mark.asyncio
    async def test_get_unwrapped(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        result = await ep.get("d1")
        assert isinstance(result, Document)

    @pytest.mark.asyncio
    async def test_upload_binary_io(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        buf = io.BytesIO(b"content")
        result = await ep.upload(buf)
        assert isinstance(result, DocumentList)

    @pytest.mark.asyncio
    async def test_upload_path(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"data")
            f.flush()
            result = await ep.upload(f.name)
        assert isinstance(result, DocumentList)

    @pytest.mark.asyncio
    async def test_upload_unwrapped(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        buf = io.BytesIO(b"content")
        result = await ep.upload(buf)
        assert len(result.documents) == 1

    @pytest.mark.asyncio
    async def test_update_info(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        result = await ep.update_info("d1", title="T", validate=False)
        assert isinstance(result, Document)

    @pytest.mark.asyncio
    async def test_update_recipient(self):
        ep, req = self._make()
        req.return_value = None
        await ep.update_recipient("d1", edrpou="e", email="e@m.com", validate=False)

    @pytest.mark.asyncio
    async def test_update_access_settings(self):
        ep, req = self._make()
        req.return_value = None
        await ep.update_access_settings("d1", level="extended")

    @pytest.mark.asyncio
    async def test_update_viewers_with_groups_and_roles(self):
        ep, req = self._make()
        req.return_value = None
        await ep.update_viewers("d1", strategy="add", groups_ids=["g1"], roles_ids=["r1"])
        call_json = req.call_args.kwargs["json"]
        assert "groups_ids" in call_json

    @pytest.mark.asyncio
    async def test_update_viewers_without_optional(self):
        ep, req = self._make()
        req.return_value = None
        await ep.update_viewers("d1", strategy="replace")
        call_json = req.call_args.kwargs["json"]
        assert "groups_ids" not in call_json

    @pytest.mark.asyncio
    async def test_set_flow(self):
        ep, req = self._make()
        req.return_value = None
        await ep.set_flow("d1", [{"edrpou": "e", "order": 1}], validate=False)
        req.assert_called_once()
        assert req.call_args.kwargs["json"] == [{"edrpou": "e", "order": 1}]

    @pytest.mark.asyncio
    async def test_list_incoming(self):
        ep, req = self._make()
        req.return_value = INCOMING_DOC_LIST_DATA
        result = await ep.list_incoming()
        assert isinstance(result, AsyncCursorPage)
        assert len(result.data) == 1
        assert result.documents == result.data

    @pytest.mark.asyncio
    async def test_set_signers(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        await ep.set_signers("d1", signer_entities=[], validate=False)

    @pytest.mark.asyncio
    async def test_download_original(self):
        ep, req = self._make()
        req.return_value = b"bytes"
        assert await ep.download_original("d1") == b"bytes"

    @pytest.mark.asyncio
    async def test_download_original_with_version(self):
        ep, req = self._make()
        req.return_value = b"bytes"
        await ep.download_original("d1", version="v1")
        req.assert_called_with("GET", "/api/v2/documents/d1/original", params={"version": "v1"})

    @pytest.mark.asyncio
    async def test_download_archive(self):
        ep, req = self._make()
        req.return_value = b"zip"
        assert await ep.download_archive("d1") == b"zip"

    @pytest.mark.asyncio
    async def test_download_p7s(self):
        ep, req = self._make()
        req.return_value = b"p7s"
        assert await ep.download_p7s("d1") == b"p7s"

    @pytest.mark.asyncio
    async def test_download_asic(self):
        ep, req = self._make()
        req.return_value = b"asic"
        assert await ep.download_asic("d1") == b"asic"

    @pytest.mark.asyncio
    async def test_download_documents(self):
        ep, req = self._make()
        req.return_value = {"documents": [{"id": "d1"}]}
        result = await ep.download_documents(["d1"])
        assert isinstance(result, DownloadDocumentList)

    @pytest.mark.asyncio
    async def test_xml_to_pdf_create(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.xml_to_pdf_create("d1")

    @pytest.mark.asyncio
    async def test_xml_to_pdf_download(self):
        ep, req = self._make()
        req.return_value = b"pdf"
        assert await ep.xml_to_pdf_download("d1") == b"pdf"

    @pytest.mark.asyncio
    async def test_pdf_print(self):
        ep, req = self._make()
        req.return_value = b"pdf"
        assert await ep.pdf_print("d1") == b"pdf"

    @pytest.mark.asyncio
    async def test_statuses(self):
        ep, req = self._make()
        req.return_value = {"data_list": []}
        result = await ep.statuses(["d1"])
        assert isinstance(result, DocumentStatusList)

    @pytest.mark.asyncio
    async def test_reject(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.reject("d1", text="reason", validate=False)

    @pytest.mark.asyncio
    async def test_send(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.send("d1", validate=False)

    @pytest.mark.asyncio
    async def test_delete(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.delete("d1", validate=False)

    @pytest.mark.asyncio
    async def test_archive_with_directory(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.archive(["d1"], directory_id="dir1")
        call_json = req.call_args.kwargs["json"]
        assert call_json["directory_id"] == "dir1"

    @pytest.mark.asyncio
    async def test_archive_without_directory(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.archive(["d1"])
        call_json = req.call_args.kwargs["json"]
        assert "directory_id" not in call_json

    @pytest.mark.asyncio
    async def test_unarchive(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.unarchive(["d1"])

    @pytest.mark.asyncio
    async def test_mark_as_processed(self):
        ep, req = self._make()
        req.return_value = {"updated_ids": ["d1"]}
        result = await ep.mark_as_processed(["d1"])
        assert isinstance(result, UpdatedIds)

    @pytest.mark.asyncio
    async def test_structured_data_download(self):
        ep, req = self._make()
        req.return_value = {"details": {}}
        await ep.structured_data_download("d1")

    @pytest.mark.asyncio
    async def test_download_archive_with_instruction(self):
        ep, req = self._make()
        req.return_value = b"zip-data"
        await ep.download_archive("d1", with_instruction=1)
        assert req.call_args.kwargs["params"] == {"with_instruction": 1}

    @pytest.mark.asyncio
    async def test_statuses_rejects_over_500(self):
        ep, _ = self._make()
        with pytest.raises(ValueError, match="500"):
            await ep.statuses(["id"] * 501)

    @pytest.mark.asyncio
    async def test_upload_recipient_edrpou(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"test")
            f.flush()
            path = f.name
        try:
            await ep.upload(path, recipient_edrpou="12345678")
            # recipient_edrpou is resolved to 'edrpou' query param by collect_params
            call_params = req.call_args.kwargs.get("params", {})
            assert call_params.get("edrpou") == "12345678"
        finally:
            import os

            os.unlink(path)


# -- State validation tests ------------------------------------------------

_VALIDATED_METHODS = [
    ("send", {"validate": True}, "send"),
    ("reject", {"text": "reason", "validate": True}, "reject"),
    ("delete", {"validate": True}, "delete"),
    ("update_info", {"title": "T", "validate": True}, "update_info"),
    ("update_recipient", {"edrpou": "e", "email": "e@m", "validate": True}, "update_recipient"),
    ("set_flow", None, "set_flow"),  # positional arg handled separately
    ("set_signers", {"signer_entities": [], "validate": True}, "set_signers"),
]


class TestAsyncDocumentsStateValidation:
    """Tests for implicit FSM validation in lifecycle methods."""

    def _make(self) -> tuple[AsyncDocuments, AsyncMock]:
        transport = MagicMock()
        ep = AsyncDocuments(transport)
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_send_allowed_status(self):
        """send() should succeed when document status allows it (7001)."""
        ep, req = self._make()
        req.side_effect = [{"id": "d1", "status": 7001}, {}]
        await ep.send("d1")
        assert req.call_count == 2  # GET (validate) + POST (send)

    @pytest.mark.asyncio
    async def test_send_forbidden_status(self):
        """send() should raise DocumentStateError for status 7008 (fully signed)."""
        ep, req = self._make()
        req.return_value = {"id": "d1", "status": 7008}
        with pytest.raises(DocumentStateError, match="send"):
            await ep.send("d1")

    @pytest.mark.asyncio
    async def test_send_skip_validation(self):
        """send(validate=False) should skip the GET call."""
        ep, req = self._make()
        req.return_value = {}
        await ep.send("d1", validate=False)
        req.assert_called_once_with("POST", "/api/v2/documents/d1/send")

    @pytest.mark.asyncio
    async def test_reject_allowed_status(self):
        ep, req = self._make()
        req.side_effect = [{"id": "d1", "status": 7001}, {}]
        await ep.reject("d1", text="reason")
        assert req.call_count == 2

    @pytest.mark.asyncio
    async def test_reject_forbidden_status(self):
        ep, req = self._make()
        req.return_value = {"id": "d1", "status": 7008}
        with pytest.raises(DocumentStateError, match="reject"):
            await ep.reject("d1", text="reason")

    @pytest.mark.asyncio
    async def test_delete_allowed_status(self):
        ep, req = self._make()
        req.side_effect = [{"id": "d1", "status": 7000}, {}]
        await ep.delete("d1")
        assert req.call_count == 2

    @pytest.mark.asyncio
    async def test_delete_forbidden_status(self):
        ep, req = self._make()
        req.return_value = {"id": "d1", "status": 7002}
        with pytest.raises(DocumentStateError, match="delete"):
            await ep.delete("d1")

    @pytest.mark.asyncio
    async def test_update_info_allowed_status(self):
        ep, req = self._make()
        req.side_effect = [{"id": "d1", "status": 7000}, {"id": "d1", "status": 7000}]
        result = await ep.update_info("d1", title="T")
        assert isinstance(result, Document)

    @pytest.mark.asyncio
    async def test_update_info_forbidden_status(self):
        ep, req = self._make()
        req.return_value = {"id": "d1", "status": 7008}
        with pytest.raises(DocumentStateError, match="update_info"):
            await ep.update_info("d1", title="T")

    @pytest.mark.asyncio
    async def test_update_recipient_allowed_status(self):
        ep, req = self._make()
        req.side_effect = [{"id": "d1", "status": 7001}, None]
        await ep.update_recipient("d1", edrpou="e", email="e@m")

    @pytest.mark.asyncio
    async def test_update_recipient_forbidden_status(self):
        ep, req = self._make()
        req.return_value = {"id": "d1", "status": 7008}
        with pytest.raises(DocumentStateError, match="update_recipient"):
            await ep.update_recipient("d1", edrpou="e", email="e@m")

    @pytest.mark.asyncio
    async def test_set_flow_allowed_status(self):
        ep, req = self._make()
        req.side_effect = [{"id": "d1", "status": 7001}, None]
        await ep.set_flow("d1", [{"edrpou": "e", "order": 1}])
        assert req.call_count == 2

    @pytest.mark.asyncio
    async def test_set_flow_forbidden_status(self):
        ep, req = self._make()
        req.return_value = {"id": "d1", "status": 7008}
        with pytest.raises(DocumentStateError, match="set_flow"):
            await ep.set_flow("d1", [{"edrpou": "e", "order": 1}])

    @pytest.mark.asyncio
    async def test_set_signers_allowed_status(self):
        ep, req = self._make()
        req.side_effect = [{"id": "d1", "status": 7001}, None]
        await ep.set_signers("d1", signer_entities=[])
        assert req.call_count == 2

    @pytest.mark.asyncio
    async def test_set_signers_forbidden_status(self):
        ep, req = self._make()
        req.return_value = {"id": "d1", "status": 7008}
        with pytest.raises(DocumentStateError, match="set_signers"):
            await ep.set_signers("d1", signer_entities=[])

    @pytest.mark.asyncio
    async def test_unknown_status_allows_everything(self):
        """Unknown statuses should not block any operation."""
        ep, req = self._make()
        req.side_effect = [{"id": "d1", "status": 9999}, {}]
        await ep.send("d1")  # should not raise
        assert req.call_count == 2
