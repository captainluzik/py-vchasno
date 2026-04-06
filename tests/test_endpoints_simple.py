"""Tests for simple endpoint groups (categories, signatures, groups, reviews,
billing, children, templates, comments, fields, reports, roles, delete_requests, tags, versions)."""

from __future__ import annotations

import io
import tempfile
from unittest.mock import AsyncMock, MagicMock

import pytest

from vchasno._async.endpoints.billing import AsyncBilling
from vchasno._async.endpoints.categories import AsyncCategories
from vchasno._async.endpoints.children import AsyncChildren
from vchasno._async.endpoints.comments import AsyncComments
from vchasno._async.endpoints.delete_requests import AsyncDeleteRequests
from vchasno._async.endpoints.fields import AsyncFields
from vchasno._async.endpoints.groups import AsyncGroups
from vchasno._async.endpoints.reports import AsyncReports
from vchasno._async.endpoints.reviews import AsyncReviews
from vchasno._async.endpoints.roles import AsyncRoles
from vchasno._async.endpoints.signatures import AsyncSignatures
from vchasno._async.endpoints.tags import AsyncTags
from vchasno._async.endpoints.templates import AsyncTemplates
from vchasno._async.endpoints.versions import AsyncVersions
from vchasno._sync.endpoints.billing import SyncBilling
from vchasno._sync.endpoints.categories import SyncCategories
from vchasno._sync.endpoints.children import SyncChildren
from vchasno._sync.endpoints.comments import SyncComments
from vchasno._sync.endpoints.delete_requests import SyncDeleteRequests
from vchasno._sync.endpoints.fields import SyncFields
from vchasno._sync.endpoints.groups import SyncGroups
from vchasno._sync.endpoints.reports import SyncReports
from vchasno._sync.endpoints.reviews import SyncReviews
from vchasno._sync.endpoints.roles import SyncRoles
from vchasno._sync.endpoints.signatures import SyncSignatures
from vchasno._sync.endpoints.tags import SyncTags
from vchasno._sync.endpoints.templates import SyncTemplates
from vchasno._sync.endpoints.versions import SyncVersions
from vchasno.models.common import (
    CustomField,
    DocumentCategoryInfo,
    DocumentField,
    ReportRequest,
    ReportStatus,
    Template,
    UpdatedIds,
)
from vchasno.models.documents import (
    Comment,
    CommentList,
    FlowEntry,
    Review,
    ReviewRequest,
    ReviewStatus,
    SignatureDetail,
)
from vchasno.models.groups import Group, GroupMember
from vchasno.models.roles import RoleList
from vchasno.models.tags import Tag, TagList, TagRoleList

# ============================================================================
# Categories
# ============================================================================


class TestSyncCategories:
    def _make(self):
        ep = SyncCategories(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_list(self):
        ep, req = self._make()
        req.return_value = [{"category_id": 1, "category_title": "T", "is_public": True}]
        result = ep.list()
        assert len(result) == 1
        assert isinstance(result[0], DocumentCategoryInfo)

    def test_create(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.create(title="New Cat")
        req.assert_called_once_with("POST", "/api/v2/document-categories", json={"title": "New Cat"})

    def test_update(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.update(1, title="Updated")
        req.assert_called_once()

    def test_delete(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.delete(1)
        req.assert_called_once()


class TestAsyncCategories:
    def _make(self):
        ep = AsyncCategories(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_list(self):
        ep, req = self._make()
        req.return_value = [{"category_id": 1, "category_title": "T", "is_public": True}]
        result = await ep.list()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_create(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.create(title="X")

    @pytest.mark.asyncio
    async def test_update(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.update(1, title="X")

    @pytest.mark.asyncio
    async def test_delete(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.delete(1)


# ============================================================================
# Signatures
# ============================================================================


class TestSyncSignatures:
    def _make(self):
        ep = SyncSignatures(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_list(self):
        ep, req = self._make()
        req.return_value = [{"id": "s1"}]
        result = ep.list("d1")
        assert len(result) == 1
        assert isinstance(result[0], SignatureDetail)

    def test_add_without_stamp(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.add("d1", signature="sig")
        call_json = req.call_args.kwargs["json"]
        assert "stamp" not in call_json

    def test_add_with_stamp(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.add("d1", signature="sig", stamp="stp")
        call_json = req.call_args.kwargs["json"]
        assert call_json["stamp"] == "stp"

    def test_flows(self):
        ep, req = self._make()
        req.return_value = [{"edrpou": "e", "order": 1}]
        result = ep.flows("d1")
        assert len(result) == 1
        assert isinstance(result[0], FlowEntry)


class TestAsyncSignatures:
    def _make(self):
        ep = AsyncSignatures(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_list(self):
        ep, req = self._make()
        req.return_value = [{"id": "s1"}]
        result = await ep.list("d1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_add_with_stamp(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.add("d1", signature="sig", stamp="stp")
        call_json = req.call_args.kwargs["json"]
        assert call_json["stamp"] == "stp"

    @pytest.mark.asyncio
    async def test_add_without_stamp(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.add("d1", signature="sig")
        call_json = req.call_args.kwargs["json"]
        assert "stamp" not in call_json

    @pytest.mark.asyncio
    async def test_flows(self):
        ep, req = self._make()
        req.return_value = [{"edrpou": "e"}]
        result = await ep.flows("d1")
        assert len(result) == 1


# ============================================================================
# Groups
# ============================================================================


class TestSyncGroups:
    def _make(self):
        ep = SyncGroups(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_list(self):
        ep, req = self._make()
        req.return_value = [{"id": "g1", "name": "G"}]
        result = ep.list()
        assert len(result) == 1
        assert isinstance(result[0], Group)

    def test_get(self):
        ep, req = self._make()
        req.return_value = {"id": "g1", "name": "G"}
        result = ep.get("g1")
        assert isinstance(result, Group)

    def test_create(self):
        ep, req = self._make()
        req.return_value = {"id": "g1", "name": "New"}
        result = ep.create(name="New")
        assert isinstance(result, Group)

    def test_update(self):
        ep, req = self._make()
        req.return_value = {"id": "g1", "name": "Updated"}
        result = ep.update("g1", name="Updated")
        assert isinstance(result, Group)

    def test_delete(self):
        ep, req = self._make()
        req.return_value = {}
        ep.delete("g1")

    def test_members(self):
        ep, req = self._make()
        req.return_value = [{"id": "m1", "role_id": "r1", "group_id": "g1"}]
        result = ep.members("g1")
        assert len(result) == 1
        assert isinstance(result[0], GroupMember)

    def test_add_members(self):
        ep, req = self._make()
        req.return_value = [{"id": "m1", "role_id": "r1", "group_id": "g1"}]
        result = ep.add_members("g1", role_ids=["r1"])
        assert len(result) == 1

    def test_remove_members(self):
        ep, req = self._make()
        req.return_value = {}
        ep.remove_members("g1", group_members=["m1"])


class TestAsyncGroups:
    def _make(self):
        ep = AsyncGroups(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_list(self):
        ep, req = self._make()
        req.return_value = [{"id": "g1", "name": "G"}]
        assert len(await ep.list()) == 1

    @pytest.mark.asyncio
    async def test_get(self):
        ep, req = self._make()
        req.return_value = {"id": "g1", "name": "G"}
        assert isinstance(await ep.get("g1"), Group)

    @pytest.mark.asyncio
    async def test_create(self):
        ep, req = self._make()
        req.return_value = {"id": "g1", "name": "N"}
        assert isinstance(await ep.create(name="N"), Group)

    @pytest.mark.asyncio
    async def test_update(self):
        ep, req = self._make()
        req.return_value = {"id": "g1", "name": "U"}
        assert isinstance(await ep.update("g1", name="U"), Group)

    @pytest.mark.asyncio
    async def test_delete(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.delete("g1")

    @pytest.mark.asyncio
    async def test_members(self):
        ep, req = self._make()
        req.return_value = [{"id": "m1", "role_id": "r1", "group_id": "g1"}]
        assert len(await ep.members("g1")) == 1

    @pytest.mark.asyncio
    async def test_add_members(self):
        ep, req = self._make()
        req.return_value = [{"id": "m1", "role_id": "r1", "group_id": "g1"}]
        assert len(await ep.add_members("g1", role_ids=["r1"])) == 1

    @pytest.mark.asyncio
    async def test_remove_members(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.remove_members("g1", group_members=["m1"])


# ============================================================================
# Reviews
# ============================================================================


class TestSyncReviews:
    def _make(self):
        ep = SyncReviews(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_history(self):
        ep, req = self._make()
        req.return_value = [{"user_email": "e"}]
        result = ep.history("d1")
        assert len(result) == 1
        assert isinstance(result[0], Review)

    def test_requests(self):
        ep, req = self._make()
        req.return_value = [{"user_from_email": "f"}]
        result = ep.requests("d1")
        assert len(result) == 1
        assert isinstance(result[0], ReviewRequest)

    def test_status(self):
        ep, req = self._make()
        req.return_value = {"status": "approved"}
        result = ep.status("d1")
        assert isinstance(result, ReviewStatus)

    def test_add_reviewer_with_email(self):
        ep, req = self._make()
        req.return_value = {}
        ep.add_reviewer("d1", user_to_email="e@m.com")
        call_json = req.call_args.kwargs["json"]
        assert call_json["user_to_email"] == "e@m.com"

    def test_add_reviewer_with_group(self):
        ep, req = self._make()
        req.return_value = {}
        ep.add_reviewer("d1", group_to_name="G", is_parallel=False)
        call_json = req.call_args.kwargs["json"]
        assert call_json["group_to_name"] == "G"
        assert call_json["is_parallel"] is False

    def test_add_reviewer_no_optional(self):
        ep, req = self._make()
        req.return_value = {}
        ep.add_reviewer("d1")
        call_json = req.call_args.kwargs["json"]
        assert "user_to_email" not in call_json
        assert "group_to_name" not in call_json

    def test_remove_reviewer_with_email(self):
        ep, req = self._make()
        req.return_value = {}
        ep.remove_reviewer("d1", user_to_email="e@m.com")
        call_json = req.call_args.kwargs["json"]
        assert call_json["user_to_email"] == "e@m.com"

    def test_remove_reviewer_with_group(self):
        ep, req = self._make()
        req.return_value = {}
        ep.remove_reviewer("d1", group_to_name="G")
        call_json = req.call_args.kwargs["json"]
        assert call_json["group_to_name"] == "G"

    def test_remove_reviewer_no_optional(self):
        ep, req = self._make()
        req.return_value = {}
        ep.remove_reviewer("d1")
        call_json = req.call_args.kwargs["json"]
        assert "user_to_email" not in call_json
        assert "group_to_name" not in call_json


class TestAsyncReviews:
    def _make(self):
        ep = AsyncReviews(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_history(self):
        ep, req = self._make()
        req.return_value = [{}]
        assert len(await ep.history("d1")) == 1

    @pytest.mark.asyncio
    async def test_requests(self):
        ep, req = self._make()
        req.return_value = [{}]
        assert len(await ep.requests("d1")) == 1

    @pytest.mark.asyncio
    async def test_status(self):
        ep, req = self._make()
        req.return_value = {"status": "pending"}
        assert isinstance(await ep.status("d1"), ReviewStatus)

    @pytest.mark.asyncio
    async def test_add_reviewer_with_email(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.add_reviewer("d1", user_to_email="e@m.com")

    @pytest.mark.asyncio
    async def test_add_reviewer_with_group(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.add_reviewer("d1", group_to_name="G")

    @pytest.mark.asyncio
    async def test_add_reviewer_no_optional(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.add_reviewer("d1")
        call_json = req.call_args.kwargs["json"]
        assert "user_to_email" not in call_json

    @pytest.mark.asyncio
    async def test_remove_reviewer_with_email(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.remove_reviewer("d1", user_to_email="e@m.com")

    @pytest.mark.asyncio
    async def test_remove_reviewer_with_group(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.remove_reviewer("d1", group_to_name="G")

    @pytest.mark.asyncio
    async def test_remove_reviewer_no_optional(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.remove_reviewer("d1")
        call_json = req.call_args.kwargs["json"]
        assert "user_to_email" not in call_json


# ============================================================================
# Billing
# ============================================================================


class TestSyncBilling:
    def test_activate_trial_default(self):
        ep = SyncBilling(MagicMock())
        ep._request = MagicMock(return_value={})
        ep.activate_trial()
        ep._request.assert_called_with(
            "POST", "/api/v2/billing/companies/rates/trials", json={"rate": "integration_trial"}
        )

    def test_activate_trial_custom(self):
        ep = SyncBilling(MagicMock())
        ep._request = MagicMock(return_value={})
        ep.activate_trial(rate="custom")
        ep._request.assert_called_with("POST", "/api/v2/billing/companies/rates/trials", json={"rate": "custom"})


class TestAsyncBilling:
    @pytest.mark.asyncio
    async def test_activate_trial(self):
        ep = AsyncBilling(MagicMock())
        ep._request = AsyncMock(return_value={})
        await ep.activate_trial()
        ep._request.assert_called_with(
            "POST", "/api/v2/billing/companies/rates/trials", json={"rate": "integration_trial"}
        )


# ============================================================================
# Children
# ============================================================================


class TestSyncChildren:
    def test_add(self):
        ep = SyncChildren(MagicMock())
        ep._request = MagicMock(return_value={})
        ep.add("p1", "c1")
        ep._request.assert_called_with("POST", "/api/v2/documents/p1/child/c1")

    def test_remove(self):
        ep = SyncChildren(MagicMock())
        ep._request = MagicMock(return_value={})
        ep.remove("p1", "c1")
        ep._request.assert_called_with("DELETE", "/api/v2/documents/p1/child/c1")


class TestAsyncChildren:
    @pytest.mark.asyncio
    async def test_add(self):
        ep = AsyncChildren(MagicMock())
        ep._request = AsyncMock(return_value={})
        await ep.add("p1", "c1")

    @pytest.mark.asyncio
    async def test_remove(self):
        ep = AsyncChildren(MagicMock())
        ep._request = AsyncMock(return_value={})
        await ep.remove("p1", "c1")


# ============================================================================
# Templates
# ============================================================================


class TestSyncTemplates:
    def test_list(self):
        ep = SyncTemplates(MagicMock())
        ep._request = MagicMock(return_value=[{"id": "t1", "name": "T"}])
        result = ep.list()
        assert len(result) == 1
        assert isinstance(result[0], Template)

    def test_get(self):
        ep = SyncTemplates(MagicMock())
        ep._request = MagicMock(return_value={"id": "t1", "name": "T"})
        result = ep.get("t1")
        assert isinstance(result, Template)


class TestAsyncTemplates:
    @pytest.mark.asyncio
    async def test_list(self):
        ep = AsyncTemplates(MagicMock())
        ep._request = AsyncMock(return_value=[{"id": "t1", "name": "T"}])
        assert len(await ep.list()) == 1

    @pytest.mark.asyncio
    async def test_get(self):
        ep = AsyncTemplates(MagicMock())
        ep._request = AsyncMock(return_value={"id": "t1", "name": "T"})
        assert isinstance(await ep.get("t1"), Template)


# ============================================================================
# Comments
# ============================================================================


class TestSyncComments:
    def _make(self):
        ep = SyncComments(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_list(self):
        ep, req = self._make()
        req.return_value = {"comments": [{"id": "c1"}], "next_cursor": None}
        result = ep.list(document_id="d1")
        assert isinstance(result, CommentList)

    def test_list_for_document_wrapped(self):
        ep, req = self._make()
        req.return_value = {"comments": [{"id": "c1"}]}
        result = ep.list_for_document("d1")
        assert len(result) == 1
        assert isinstance(result[0], Comment)

    def test_list_for_document_unwrapped(self):
        ep, req = self._make()
        req.return_value = [{"id": "c1"}]
        result = ep.list_for_document("d1")
        assert len(result) == 1

    def test_add(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.add("d1", text="hello", is_internal=True)
        call_json = req.call_args.kwargs["json"]
        assert call_json["is_internal"] is True


class TestAsyncComments:
    def _make(self):
        ep = AsyncComments(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_list(self):
        ep, req = self._make()
        req.return_value = {"comments": [], "next_cursor": None}
        result = await ep.list()
        assert isinstance(result, CommentList)

    @pytest.mark.asyncio
    async def test_list_for_document_wrapped(self):
        ep, req = self._make()
        req.return_value = {"comments": [{"id": "c1"}]}
        result = await ep.list_for_document("d1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_for_document_unwrapped(self):
        ep, req = self._make()
        req.return_value = [{"id": "c1"}]
        result = await ep.list_for_document("d1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_add(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.add("d1", text="hello")


# ============================================================================
# Fields
# ============================================================================


class TestSyncFields:
    def _make(self):
        ep = SyncFields(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_list(self):
        ep, req = self._make()
        req.return_value = [{"id": "f1", "name": "F", "type": "text"}]
        result = ep.list()
        assert isinstance(result[0], CustomField)

    def test_create(self):
        ep, req = self._make()
        req.return_value = {"id": "f1", "name": "F", "type": "text"}
        result = ep.create(name="F", field_type="text", is_required=True)
        assert isinstance(result, CustomField)

    def test_list_for_document(self):
        ep, req = self._make()
        req.return_value = [{"field_id": "f1", "name": "F", "type": "text", "is_required": True}]
        result = ep.list_for_document("d1")
        assert isinstance(result[0], DocumentField)

    def test_add_to_document(self):
        ep, req = self._make()
        req.return_value = {}
        ep.add_to_document("d1", field_id="f1", value="v", is_required=True)


class TestAsyncFields:
    def _make(self):
        ep = AsyncFields(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_list(self):
        ep, req = self._make()
        req.return_value = [{"id": "f1", "name": "F", "type": "text"}]
        assert len(await ep.list()) == 1

    @pytest.mark.asyncio
    async def test_create(self):
        ep, req = self._make()
        req.return_value = {"id": "f1", "name": "F", "type": "text"}
        result = await ep.create(name="F", field_type="text")
        assert isinstance(result, CustomField)

    @pytest.mark.asyncio
    async def test_list_for_document(self):
        ep, req = self._make()
        req.return_value = [{"field_id": "f1", "name": "F", "type": "text", "is_required": True}]
        assert len(await ep.list_for_document("d1")) == 1

    @pytest.mark.asyncio
    async def test_add_to_document(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.add_to_document("d1", field_id="f1", value="v")


# ============================================================================
# Reports
# ============================================================================


class TestSyncReports:
    def _make(self):
        ep = SyncReports(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_request_document_actions(self):
        ep, req = self._make()
        req.return_value = {"report_id": "r1"}
        result = ep.request_document_actions(date_from="2024-01-01", date_to="2024-12-31")
        assert isinstance(result, ReportRequest)

    def test_request_user_actions(self):
        ep, req = self._make()
        req.return_value = {"report_id": "r1"}
        result = ep.request_user_actions(date_from="2024-01-01", date_to="2024-12-31")
        assert isinstance(result, ReportRequest)

    def test_status(self):
        ep, req = self._make()
        req.return_value = {"status": "ready", "filename": "report.csv"}
        result = ep.status("r1")
        assert isinstance(result, ReportStatus)

    def test_download(self):
        ep, req = self._make()
        req.return_value = b"csv data"
        assert ep.download("r1") == b"csv data"


class TestAsyncReports:
    def _make(self):
        ep = AsyncReports(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_request_document_actions(self):
        ep, req = self._make()
        req.return_value = {"report_id": "r1"}
        assert isinstance(await ep.request_document_actions(date_from="d", date_to="d"), ReportRequest)

    @pytest.mark.asyncio
    async def test_request_user_actions(self):
        ep, req = self._make()
        req.return_value = {"report_id": "r1"}
        assert isinstance(await ep.request_user_actions(date_from="d", date_to="d"), ReportRequest)

    @pytest.mark.asyncio
    async def test_status(self):
        ep, req = self._make()
        req.return_value = {"status": "ready"}
        assert isinstance(await ep.status("r1"), ReportStatus)

    @pytest.mark.asyncio
    async def test_download(self):
        ep, req = self._make()
        req.return_value = b"data"
        assert await ep.download("r1") == b"data"


# ============================================================================
# Roles
# ============================================================================


class TestSyncRoles:
    def _make(self):
        ep = SyncRoles(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_list(self):
        ep, req = self._make()
        req.return_value = {"roles": [{"id": "r1"}]}
        result = ep.list()
        assert isinstance(result, RoleList)

    def test_update(self):
        ep, req = self._make()
        req.return_value = {}
        ep.update("r1", position="dev")
        req.assert_called_with("PATCH", "/api/v2/roles/r1", json={"position": "dev"})

    def test_delete(self):
        ep, req = self._make()
        req.return_value = {}
        ep.delete("r1")

    def test_invite_coworkers(self):
        ep, req = self._make()
        req.return_value = {}
        ep.invite_coworkers(emails=["e@m.com"])

    def test_create_coworker_minimal(self):
        ep, req = self._make()
        req.return_value = {}
        ep.create_coworker(email="e@m.com")
        call_json = req.call_args.kwargs["json"]
        assert "first_name" not in call_json

    def test_create_coworker_full(self):
        ep, req = self._make()
        req.return_value = {}
        ep.create_coworker(email="e@m.com", first_name="F", second_name="S", last_name="L", phone="+1")
        call_json = req.call_args.kwargs["json"]
        assert call_json["first_name"] == "F"
        assert call_json["phone"] == "+1"

    def test_create_tokens_minimal(self):
        ep, req = self._make()
        req.return_value = {}
        ep.create_tokens(emails=["e@m.com"])
        call_json = req.call_args.kwargs["json"]
        assert "expire_days" not in call_json

    def test_create_tokens_with_expire(self):
        ep, req = self._make()
        req.return_value = {}
        ep.create_tokens(emails=["e@m.com"], expire_days="30")
        call_json = req.call_args.kwargs["json"]
        assert call_json["expire_days"] == "30"

    def test_delete_tokens(self):
        ep, req = self._make()
        req.return_value = {}
        ep.delete_tokens(emails=["e@m.com"])


class TestAsyncRoles:
    def _make(self):
        ep = AsyncRoles(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_list(self):
        ep, req = self._make()
        req.return_value = {"roles": [{"id": "r1"}]}
        assert isinstance(await ep.list(), RoleList)

    @pytest.mark.asyncio
    async def test_update(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.update("r1", position="dev")

    @pytest.mark.asyncio
    async def test_delete(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.delete("r1")

    @pytest.mark.asyncio
    async def test_invite_coworkers(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.invite_coworkers(emails=["e@m.com"])

    @pytest.mark.asyncio
    async def test_create_coworker_minimal(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.create_coworker(email="e@m.com")
        call_json = req.call_args.kwargs["json"]
        assert "first_name" not in call_json

    @pytest.mark.asyncio
    async def test_create_coworker_full(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.create_coworker(email="e@m.com", first_name="F", second_name="S", last_name="L", phone="+1")
        call_json = req.call_args.kwargs["json"]
        assert call_json["last_name"] == "L"

    @pytest.mark.asyncio
    async def test_create_tokens_minimal(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.create_tokens(emails=["e@m.com"])

    @pytest.mark.asyncio
    async def test_create_tokens_with_expire(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.create_tokens(emails=["e@m.com"], expire_days="30")

    @pytest.mark.asyncio
    async def test_delete_tokens(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.delete_tokens(emails=["e@m.com"])


# ============================================================================
# Delete Requests
# ============================================================================


class TestSyncDeleteRequests:
    def _make(self):
        ep = SyncDeleteRequests(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_create(self):
        ep, req = self._make()
        req.return_value = {}
        ep.create("d1", message="reason")

    def test_cancel(self):
        ep, req = self._make()
        req.return_value = {}
        ep.cancel("d1")

    def test_accept(self):
        ep, req = self._make()
        req.return_value = {}
        ep.accept("d1")

    def test_reject(self):
        ep, req = self._make()
        req.return_value = {}
        ep.reject("d1", reject_message="no")

    def test_list_returns_list(self):
        ep, req = self._make()
        req.return_value = [{"id": "dr1"}]
        result = ep.list(status="new")
        assert isinstance(result, list)

    def test_list_wraps_non_list(self):
        ep, req = self._make()
        req.return_value = {"id": "dr1"}
        result = ep.list()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_lock_delete(self):
        ep, req = self._make()
        req.return_value = {"updated_ids": ["d1"]}
        result = ep.lock_delete(["d1"])
        assert isinstance(result, UpdatedIds)

    def test_unlock_delete(self):
        ep, req = self._make()
        req.return_value = {"updated_ids": ["d1"]}
        result = ep.unlock_delete(["d1"])
        assert isinstance(result, UpdatedIds)


class TestAsyncDeleteRequests:
    def _make(self):
        ep = AsyncDeleteRequests(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_create(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.create("d1", message="reason")

    @pytest.mark.asyncio
    async def test_cancel(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.cancel("d1")

    @pytest.mark.asyncio
    async def test_accept(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.accept("d1")

    @pytest.mark.asyncio
    async def test_reject(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.reject("d1", reject_message="no")

    @pytest.mark.asyncio
    async def test_list_returns_list(self):
        ep, req = self._make()
        req.return_value = [{"id": "dr1"}]
        result = await ep.list()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_list_wraps_non_list(self):
        ep, req = self._make()
        req.return_value = {"id": "dr1"}
        result = await ep.list()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_lock_delete(self):
        ep, req = self._make()
        req.return_value = {"updated_ids": ["d1"]}
        result = await ep.lock_delete(["d1"])
        assert isinstance(result, UpdatedIds)

    @pytest.mark.asyncio
    async def test_unlock_delete(self):
        ep, req = self._make()
        req.return_value = {"updated_ids": ["d1"]}
        result = await ep.unlock_delete(["d1"])
        assert isinstance(result, UpdatedIds)


# ============================================================================
# Tags
# ============================================================================


class TestSyncTags:
    def _make(self):
        ep = SyncTags(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_list_no_params(self):
        ep, req = self._make()
        req.return_value = {"tags": [{"id": "t1", "name": "T"}]}
        result = ep.list()
        assert isinstance(result, TagList)
        req.assert_called_with("GET", "/api/v2/tags", params=None)

    def test_list_with_params(self):
        ep, req = self._make()
        req.return_value = {"tags": []}
        ep.list(limit=10, offset=5)
        req.assert_called_with("GET", "/api/v2/tags", params={"limit": 10, "offset": 5})

    def test_roles(self):
        ep, req = self._make()
        req.return_value = {"roles": []}
        result = ep.roles("t1")
        assert isinstance(result, TagRoleList)

    def test_create_for_documents(self):
        ep, req = self._make()
        req.return_value = [{"id": "t1", "name": "T"}]
        result = ep.create_for_documents(documents_ids=["d1"], names=["Tag1"])
        assert isinstance(result[0], Tag)

    def test_connect_documents(self):
        ep, req = self._make()
        req.return_value = {}
        ep.connect_documents(documents_ids=["d1"], tags_ids=["t1"])

    def test_disconnect_documents(self):
        ep, req = self._make()
        req.return_value = {}
        ep.disconnect_documents(documents_ids=["d1"], tags_ids=["t1"])

    def test_create_for_roles(self):
        ep, req = self._make()
        req.return_value = [{"id": "t1", "name": "T"}]
        result = ep.create_for_roles(roles_ids=["r1"], names=["Tag1"])
        assert isinstance(result[0], Tag)

    def test_connect_roles(self):
        ep, req = self._make()
        req.return_value = {}
        ep.connect_roles(roles_ids=["r1"], tags_ids=["t1"])

    def test_disconnect_roles(self):
        ep, req = self._make()
        req.return_value = {}
        ep.disconnect_roles(roles_ids=["r1"], tags_ids=["t1"])


class TestAsyncTags:
    def _make(self):
        ep = AsyncTags(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_list_no_params(self):
        ep, req = self._make()
        req.return_value = {"tags": []}
        result = await ep.list()
        assert isinstance(result, TagList)

    @pytest.mark.asyncio
    async def test_list_with_params(self):
        ep, req = self._make()
        req.return_value = {"tags": []}
        await ep.list(limit=10, offset=5)
        req.assert_called_with("GET", "/api/v2/tags", params={"limit": 10, "offset": 5})

    @pytest.mark.asyncio
    async def test_roles(self):
        ep, req = self._make()
        req.return_value = {"roles": []}
        assert isinstance(await ep.roles("t1"), TagRoleList)

    @pytest.mark.asyncio
    async def test_create_for_documents(self):
        ep, req = self._make()
        req.return_value = [{"id": "t1", "name": "T"}]
        result = await ep.create_for_documents(documents_ids=["d1"], names=["T"])
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_connect_documents(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.connect_documents(documents_ids=["d1"], tags_ids=["t1"])

    @pytest.mark.asyncio
    async def test_disconnect_documents(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.disconnect_documents(documents_ids=["d1"], tags_ids=["t1"])

    @pytest.mark.asyncio
    async def test_create_for_roles(self):
        ep, req = self._make()
        req.return_value = [{"id": "t1", "name": "T"}]
        result = await ep.create_for_roles(roles_ids=["r1"], names=["T"])
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_connect_roles(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.connect_roles(roles_ids=["r1"], tags_ids=["t1"])

    @pytest.mark.asyncio
    async def test_disconnect_roles(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.disconnect_roles(roles_ids=["r1"], tags_ids=["t1"])


# ============================================================================
# Versions
# ============================================================================


class TestSyncVersions:
    def _make(self):
        ep = SyncVersions(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_upload_binary_io(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        buf = io.BytesIO(b"data")
        ep.upload("d1", buf)
        req.assert_called_once()

    def test_upload_binary_io_default_filename(self):
        ep, req = self._make()
        req.return_value = {}
        buf = io.BytesIO(b"data")
        ep.upload("d1", buf)
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files") or call_kwargs[1].get("files")
        assert files_arg[0][1][0] == "version"

    def test_upload_path(self):
        ep, req = self._make()
        req.return_value = {}
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"data")
            f.flush()
            ep.upload("d1", f.name)

    def test_upload_with_custom_filename(self):
        ep, req = self._make()
        req.return_value = {}
        buf = io.BytesIO(b"data")
        ep.upload("d1", buf, filename="custom.pdf")
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files") or call_kwargs[1].get("files")
        assert files_arg[0][1][0] == "custom.pdf"

    def test_delete(self):
        ep, req = self._make()
        req.return_value = {}
        ep.delete("d1", "v1")
        req.assert_called_with("DELETE", "/api/v2/documents/d1/version/v1")


class TestAsyncVersions:
    def _make(self):
        ep = AsyncVersions(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_upload_binary_io(self):
        ep, req = self._make()
        req.return_value = {}
        buf = io.BytesIO(b"data")
        await ep.upload("d1", buf)

    @pytest.mark.asyncio
    async def test_upload_path(self):
        ep, req = self._make()
        req.return_value = {}
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"data")
            f.flush()
            await ep.upload("d1", f.name)

    @pytest.mark.asyncio
    async def test_upload_binary_io_default_filename(self):
        ep, req = self._make()
        req.return_value = {}
        buf = io.BytesIO(b"data")
        await ep.upload("d1", buf)
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files") or call_kwargs[1].get("files")
        assert files_arg[0][1][0] == "version"

    @pytest.mark.asyncio
    async def test_delete(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.delete("d1", "v1")
