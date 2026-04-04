"""Tests for all Pydantic models."""

from __future__ import annotations

from vchasno.models.common import (
    CompanyCheck,
    CompanyCheckUpload,
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
    Document,
    DocumentList,
    DocumentStatusItem,
    DocumentStatusList,
    DownloadDocument,
    DownloadDocumentList,
    FlowEntry,
    IncomingDocument,
    IncomingDocumentList,
    Recipient,
    Review,
    ReviewRequest,
    ReviewStatus,
    Signature,
    SignatureDetail,
    StructuredData,
    Version,
)
from vchasno.models.groups import Group, GroupMember
from vchasno.models.cloud_signer import (
    CloudSignerRefresh,
    CloudSignerRefreshCheck,
    CloudSignerSession,
    CloudSignerSessionCheck,
    SignSession,
)
from vchasno.models.tags import Tag, TagList, TagRole, TagRoleList
from vchasno.models.archive import (
    ArchiveDirectory,
    ArchiveDirectoryList,
    ArchiveImportSignedResult,
    ArchiveScanResult,
)
from vchasno.models.roles import Role, RoleList
from vchasno.models.enums import (
    AccessSettingsLevel,
    CloudSignerSessionStatus,
    DeleteRequestStatus,
    DocumentCategory,
    DocumentStatus,
    FirstSignBy,
    ReviewState,
    SignSessionType,
    StructuredDataStatus,
    UserRole,
    ViewersStrategy,
)


# ---------------------------------------------------------------------------
# Common models
# ---------------------------------------------------------------------------

class TestDocumentCategoryInfo:
    def test_required_fields(self):
        m = DocumentCategoryInfo(category_id=1, category_title="Test", is_public=True)
        assert m.category_id == 1
        assert m.category_title == "Test"
        assert m.is_public is True
        assert m.date_updated is None

    def test_all_fields(self):
        m = DocumentCategoryInfo(category_id=2, category_title="X", is_public=False, date_updated="2024-01-01", date_created="2024-01-01")
        assert m.date_updated == "2024-01-01"


class TestCustomField:
    def test_minimal(self):
        m = CustomField(id="1", name="f", type="text")
        assert m.id == "1"
        assert m.order is None

    def test_all_fields(self):
        m = CustomField(id="1", name="f", type="text", order="1", company_id="c", is_required=True, created_by="u")
        assert m.is_required is True


class TestDocumentField:
    def test_required(self):
        m = DocumentField(field_id="1", name="f", type="text", is_required=True)
        assert m.value is None

    def test_all(self):
        m = DocumentField(field_id="1", name="f", type="text", is_required=False, value="v", date_updated="d", date_created="c")
        assert m.value == "v"


class TestTemplate:
    def test_minimal(self):
        m = Template(id="1", name="t")
        assert m.review_settings is None

    def test_full(self):
        m = Template(id="1", name="t", review_settings={"a": 1}, signers_settings={}, viewers_settings={}, fields_settings={}, tags_settings={}, created_by="u", date_created="d", date_updated="d")
        assert m.review_settings == {"a": 1}


class TestReportRequest:
    def test_fields(self):
        m = ReportRequest(report_id="r1")
        assert m.report_id == "r1"


class TestReportStatus:
    def test_minimal(self):
        m = ReportStatus(status="ready")
        assert m.filename is None

    def test_with_filename(self):
        m = ReportStatus(status="ready", filename="report.csv")
        assert m.filename == "report.csv"


class TestCompanyCheck:
    def test_fields(self):
        m = CompanyCheck(edrpou="12345678", name="Co", is_registered=True)
        assert m.is_registered is True


class TestCompanyCheckUpload:
    def test_minimal(self):
        m = CompanyCheckUpload(companies=[])
        assert m.percentage is None

    def test_full(self):
        c = CompanyCheck(edrpou="1", name="x", is_registered=False)
        m = CompanyCheckUpload(companies=[c], percentage="100", invalid_row_numbers=["1"], rows_invalid="1", rows_total="2")
        assert len(m.companies) == 1


class TestUpdatedIds:
    def test_fields(self):
        m = UpdatedIds(updated_ids=["a", "b"])
        assert len(m.updated_ids) == 2


# ---------------------------------------------------------------------------
# Document models
# ---------------------------------------------------------------------------

class TestSignature:
    def test_minimal(self):
        m = Signature(id="s1")
        assert m.email is None

    def test_full(self):
        m = Signature(id="s1", email="e@m.com", date_created="d")
        assert m.email == "e@m.com"


class TestSignatureDetail:
    def test_minimal(self):
        m = SignatureDetail(id="s1")
        assert m.edrpou is None

    def test_full(self):
        m = SignatureDetail(id="s1", edrpou="e", company_name="c", is_internal=True, role_id="r", signer_name="n", signer_position="p", serial_number="sn", timestamp="t", has_stamp=True, stamp={"k": "v"})
        assert m.has_stamp is True


class TestRecipient:
    def test_minimal(self):
        m = Recipient()
        assert m.edrpou is None

    def test_full(self):
        m = Recipient(edrpou="e", emails=["a@b.com"], name="n", is_emails_hidden=False)
        assert m.emails == ["a@b.com"]


class TestVersion:
    def test_minimal(self):
        m = Version(id="v1")
        assert m.name is None

    def test_full(self):
        m = Version(id="v1", name="n", role_id="r", date_created="d", is_sent=True, extension="pdf")
        assert m.extension == "pdf"


class TestDocument:
    def test_minimal(self):
        m = Document(id="d1", status=7000)
        assert m.title is None

    def test_full(self):
        m = Document(
            id="d1", vendor="v", vendor_id="vi", status=7008, status_text="Signed",
            signatures_to_finish=0, first_sign_by="owner", extension="pdf",
            signatures=[], title="Doc", type="contract", amount=100,
            date="2024-01-01", date_created="c", date_finished="f",
            date_delivered="d", number="N1", preview_url="pu", url="u",
            is_multilateral=False, category=1, category_details={},
            is_delivered=True, is_archived=False, is_internal=False,
            sd_status="confirmed", tags=[], recipients=[], fields=[],
            versions=[], parent=None, children=[], delete_requests=[],
            access_settings={},
        )
        assert m.status == 7008


class TestDocumentList:
    def test_fields(self):
        d = Document(id="1", status=7000)
        m = DocumentList(documents=[d], next_cursor="abc")
        assert m.next_cursor == "abc"

    def test_no_cursor(self):
        m = DocumentList(documents=[])
        assert m.next_cursor is None


class TestIncomingDocument:
    def test_minimal(self):
        m = IncomingDocument(id="i1", status=7000)
        assert m.edrpou_owner is None

    def test_full(self):
        m = IncomingDocument(
            id="i1", extension="pdf", title="T", type="t", number="N",
            status=7000, status_text="st", edrpou_owner="e", amount=1,
            company_name="cn", signatures_to_finish=0, first_sign_by="owner",
            date="d", date_created="dc", date_delivered="dd", date_finished="df",
            is_delivered=True, category=1, category_details={},
            signatures=[], preview_url="p", url="u", parent=None,
            children=[], recipients=[], fields=[], versions=[],
            is_multilateral=False, is_archived=False, sd_status="s",
            tags=[], delete_requests=[], access_settings={},
        )
        assert m.company_name == "cn"


class TestIncomingDocumentList:
    def test_fields(self):
        m = IncomingDocumentList(documents=[])
        assert m.next_cursor is None


class TestDownloadDocument:
    def test_minimal(self):
        m = DownloadDocument(id="d1")
        assert m.extension is None

    def test_full(self):
        m = DownloadDocument(id="d1", extension="pdf", archive_url="a", original_url="o", status=200, xml_to_pdf_url="x")
        assert m.archive_url == "a"


class TestDownloadDocumentList:
    def test_fields(self):
        m = DownloadDocumentList(documents=[], status=200, ready=True, pending=False, total=5)
        assert m.total == 5


class TestDocumentStatusItem:
    def test_fields(self):
        m = DocumentStatusItem(document_id="d1", status_id=7000, status_text="Uploaded")
        assert m.status_id == 7000


class TestDocumentStatusList:
    def test_fields(self):
        m = DocumentStatusList(data_list=[])
        assert m.data_list == []


class TestComment:
    def test_minimal(self):
        m = Comment(id="c1")
        assert m.text is None

    def test_full(self):
        m = Comment(id="c1", text="hi", document_id="d1", date_created="d", email="e", edrpou="e", is_internal=False, type="t", author={"name": "N"})
        assert m.author == {"name": "N"}


class TestCommentList:
    def test_fields(self):
        m = CommentList(comments=[], next_cursor="nc")
        assert m.next_cursor == "nc"


class TestReview:
    def test_minimal(self):
        m = Review()
        assert m.user_email is None

    def test_full(self):
        m = Review(user_email="e", group_name="g", is_last=True, action="approve", date_created="d")
        assert m.is_last is True


class TestReviewRequest:
    def test_fields(self):
        m = ReviewRequest(user_from_email="f", user_to_email="t", group_to_name="g", status="pending", date_created="d")
        assert m.status == "pending"


class TestReviewStatus:
    def test_fields(self):
        m = ReviewStatus(status="approved", is_required=True, date_created="d", date_updated="d")
        assert m.status == "approved"


class TestFlowEntry:
    def test_minimal(self):
        m = FlowEntry()
        assert m.edrpou is None

    def test_full(self):
        m = FlowEntry(edrpou="e", order=1, pending_signatures=2, emails=["a@b.com"])
        assert m.order == 1


class TestStructuredData:
    def test_minimal(self):
        m = StructuredData()
        assert m.details is None

    def test_full(self):
        m = StructuredData(details={"a": 1}, parties_information={"b": 2}, items=[{"c": 3}], total_price={"d": 4})
        assert m.items == [{"c": 3}]


# ---------------------------------------------------------------------------
# Group models
# ---------------------------------------------------------------------------

class TestGroup:
    def test_minimal(self):
        m = Group(id="g1", name="G")
        assert m.created_by is None

    def test_full(self):
        m = Group(id="g1", name="G", created_by="u", date_created="d", date_updated="d")
        assert m.created_by == "u"


class TestGroupMember:
    def test_fields(self):
        m = GroupMember(id="m1", role_id="r1", group_id="g1", created_by="u", date_created="d")
        assert m.role_id == "r1"


# ---------------------------------------------------------------------------
# Cloud signer models
# ---------------------------------------------------------------------------

class TestCloudSignerSession:
    def test_with_alias(self):
        m = CloudSignerSession(authSessionId="s1", isMobileLogged=True)
        assert m.auth_session_id == "s1"
        assert m.is_mobile_logged is True

    def test_with_field_name(self):
        m = CloudSignerSession(auth_session_id="s1", is_mobile_logged=False)
        assert m.auth_session_id == "s1"


class TestCloudSignerSessionCheck:
    def test_fields(self):
        m = CloudSignerSessionCheck(status="ready", token="tok")
        assert m.token == "tok"

    def test_no_token(self):
        m = CloudSignerSessionCheck(status="init")
        assert m.token is None


class TestCloudSignerRefreshCheck:
    def test_with_alias(self):
        m = CloudSignerRefreshCheck(status="ready", accessToken="at", refreshToken="rt", expiresIn=3600)
        assert m.access_token == "at"
        assert m.expires_in == 3600

    def test_minimal(self):
        m = CloudSignerRefreshCheck(status="init")
        assert m.access_token is None


class TestCloudSignerRefresh:
    def test_with_alias(self):
        m = CloudSignerRefresh(status="ok", accessToken="a", refreshToken="r", expiresIn=100)
        assert m.refresh_token == "r"

    def test_minimal(self):
        m = CloudSignerRefresh(status="ok")
        assert m.expires_in is None


class TestSignSession:
    def test_minimal(self):
        m = SignSession(id="ss1")
        assert m.document_id is None

    def test_full(self):
        m = SignSession(
            id="ss1", created_by="u", document_id="d", document_status="s",
            edrpou="e", email="e@e.com", is_legal=True, on_cancel_url="c",
            on_finish_url="f", on_document_comment_hook="ch",
            on_document_reject_hook="rh", on_document_sign_hook="sh",
            on_document_view_hook="vh", role_id="r", status="active",
            type="sign_session", url="u", vendor="v",
        )
        assert m.is_legal is True


# ---------------------------------------------------------------------------
# Tag models
# ---------------------------------------------------------------------------

class TestTag:
    def test_fields(self):
        m = Tag(id="t1", name="Tag1", date_created="d")
        assert m.name == "Tag1"

    def test_minimal(self):
        m = Tag(id="t1", name="Tag1")
        assert m.date_created is None


class TestTagList:
    def test_fields(self):
        m = TagList(tags=[Tag(id="1", name="n")])
        assert len(m.tags) == 1


class TestTagRole:
    def test_fields(self):
        m = TagRole(role_id="r1", tag_id="t1", assigner_id="a1", date_created="d")
        assert m.assigner_id == "a1"

    def test_minimal(self):
        m = TagRole(role_id="r1", tag_id="t1")
        assert m.assigner_id is None


class TestTagRoleList:
    def test_fields(self):
        m = TagRoleList(roles=[])
        assert m.roles == []


# ---------------------------------------------------------------------------
# Archive models
# ---------------------------------------------------------------------------

class TestArchiveDirectory:
    def test_fields(self):
        m = ArchiveDirectory(id=1, name="Dir")
        assert m.parent_id is None

    def test_full(self):
        m = ArchiveDirectory(id=1, parent_id=2, name="Dir", date_created="d")
        assert m.parent_id == 2


class TestArchiveDirectoryList:
    def test_fields(self):
        m = ArchiveDirectoryList(directories=[], next_cursor="c")
        assert m.next_cursor == "c"


class TestArchiveScanResult:
    def test_fields(self):
        m = ArchiveScanResult(documents=[{"id": "1"}])
        assert len(m.documents) == 1


class TestArchiveImportSignedResult:
    def test_fields(self):
        m = ArchiveImportSignedResult(document_id="d1", signature_count=2, counterparty_count=1)
        assert m.signature_count == 2


# ---------------------------------------------------------------------------
# Role models
# ---------------------------------------------------------------------------

class TestRole:
    def test_minimal(self):
        m = Role(id="r1")
        assert m.status is None

    def test_full(self):
        m = Role(id="r1", status="active", date_created="d", email="e@e.com", position="dev")
        assert m.position == "dev"


class TestRoleList:
    def test_fields(self):
        m = RoleList(roles=[Role(id="1")])
        assert len(m.roles) == 1


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TestEnums:
    def test_document_status(self):
        assert DocumentStatus.UPLOADED == 7000
        assert DocumentStatus.FULLY_SIGNED == 7008
        assert DocumentStatus.ANNULLED == 7011

    def test_document_category(self):
        assert DocumentCategory.NOT_SELECTED == 0
        assert DocumentCategory.ACT_OF_SERVICES == 1
        assert DocumentCategory.CREDIT_APPLICATION == 18891

    def test_first_sign_by(self):
        assert FirstSignBy.OWNER == "owner"
        assert FirstSignBy.RECIPIENT == "recipient"

    def test_review_state(self):
        assert ReviewState.WITHOUT_ANY == "without_any"
        assert ReviewState.PENDING == "pending"
        assert ReviewState.APPROVED == "approved"
        assert ReviewState.REJECTED == "rejected"

    def test_structured_data_status(self):
        assert StructuredDataStatus.PENDING == "pending"
        assert StructuredDataStatus.ERROR == "error"

    def test_user_role(self):
        assert UserRole.REGULAR == 8000
        assert UserRole.ADMIN == 8001

    def test_delete_request_status(self):
        assert DeleteRequestStatus.NEW == "new"
        assert DeleteRequestStatus.ACCEPTED == "accepted"

    def test_cloud_signer_session_status(self):
        assert CloudSignerSessionStatus.INIT == "init"
        assert CloudSignerSessionStatus.EXPIRED == "expired"

    def test_sign_session_type(self):
        assert SignSessionType.VIEW_SESSION == "view_session"
        assert SignSessionType.SIGN_SESSION == "sign_session"

    def test_access_settings_level(self):
        assert AccessSettingsLevel.EXTENDED == "extended"
        assert AccessSettingsLevel.PRIVATE == "private"

    def test_viewers_strategy(self):
        assert ViewersStrategy.ADD == "add"
        assert ViewersStrategy.REMOVE == "remove"
        assert ViewersStrategy.REPLACE == "replace"
