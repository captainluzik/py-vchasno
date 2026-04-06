"""Document-related models."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from vchasno.models._base import VchasnoModel


class Signature(VchasnoModel):
    """A document signature (short form from document list)."""

    id: str
    email: str | None = None
    date_created: str | None = None


class SignatureDetail(VchasnoModel):
    """Detailed signature information."""

    id: str
    edrpou: str | None = None
    company_name: str | None = None
    is_internal: bool | None = None
    role_id: str | None = None
    signer_name: str | None = None
    signer_position: str | None = None
    serial_number: str | None = None
    timestamp: str | None = None
    has_stamp: bool | None = None
    stamp: StampInfo | None = None


class StampInfo(VchasnoModel):
    """Stamp/seal information attached to a signature."""

    serial_number: str | None = None
    issuer: str | None = None
    subject: str | None = None
    acsk: str | None = None
    company_name: str | None = None
    edrpou: str | None = None
    power_type: str | None = None
    signer_name: str | None = None
    signer_position: str | None = None
    timestamp: str | None = None


class Recipient(VchasnoModel):
    """Recipient info."""

    edrpou: str | None = None
    emails: list[str] | None = None
    name: str | None = None
    is_emails_hidden: bool | None = None


class Version(VchasnoModel):
    """Document version."""

    id: str
    name: str | None = None
    role_id: str | None = None
    date_created: str | None = None
    is_sent: bool | None = None
    extension: str | None = None


class CategoryDetails(VchasnoModel):
    """Category details attached to a document."""

    category_id: int | None = None
    category_title: str | None = None
    is_public: bool | None = None


class AccessSettings(VchasnoModel):
    """Document access settings."""

    level: str | None = None


class TagRef(VchasnoModel):
    """Tag reference attached to a document."""

    id: str | None = None
    name: str | None = None


class FieldRef(VchasnoModel):
    """Custom field value reference attached to a document."""

    field_id: str | None = None
    name: str | None = None
    type: str | None = None
    value: str | None = None
    is_required: bool | None = None


class DeleteRequestRef(VchasnoModel):
    """Delete request reference attached to a document."""

    id: str | None = None
    status: str | None = None
    message: str | None = None


class _BaseDocument(VchasnoModel):
    """Shared fields between outgoing and incoming documents."""

    id: str
    extension: str | None = None
    title: str | None = None
    type: str | None = None
    number: str | None = None
    status: int
    status_text: str | None = None
    amount: int | None = None
    signatures_to_finish: int | None = None
    first_sign_by: str | None = None
    date: str | None = None
    date_created: str | None = None
    date_delivered: str | None = None
    date_finished: str | None = None
    is_delivered: bool | None = None
    category: int | None = None
    category_details: CategoryDetails | None = None
    signatures: list[Signature] | None = None
    preview_url: str | None = None
    url: str | None = None
    parent: str | None = None
    children: list[str] | None = None
    recipients: list[Recipient] | None = None
    fields: list[FieldRef] | None = None
    versions: list[Version] | None = None
    is_multilateral: bool | None = None
    is_archived: bool | None = None
    sd_status: str | None = None
    tags: list[TagRef] | None = None
    delete_requests: list[DeleteRequestRef] | None = None
    access_settings: AccessSettings | None = None


class Document(_BaseDocument):
    """Outgoing document."""

    vendor: str | None = None
    vendor_id: str | None = None
    is_internal: bool | None = None


class DocumentList(VchasnoModel):
    """Paginated list of documents."""

    documents: list[Document]
    next_cursor: str | None = None


class IncomingDocument(_BaseDocument):
    """Incoming document."""

    edrpou_owner: str | None = None
    company_name: str | None = None


class IncomingDocumentList(VchasnoModel):
    """Paginated list of incoming documents."""

    documents: list[IncomingDocument]
    next_cursor: str | None = None


class DownloadDocument(VchasnoModel):
    """Download info for a document."""

    id: str
    extension: str | None = None
    archive_url: str | None = None
    original_url: str | None = None
    status: int | None = None
    xml_to_pdf_url: str | None = None


class DownloadDocumentList(VchasnoModel):
    """Response for download-documents endpoint."""

    status: int | None = None
    ready: bool | None = None
    pending: bool | None = None
    total: int | None = None
    documents: list[DownloadDocument]


class DocumentStatusItem(VchasnoModel):
    """Single item in the statuses response."""

    document_id: str
    status_id: int
    status_text: str


class DocumentStatusList(VchasnoModel):
    """Response for POST /documents/statuses."""

    data_list: list[DocumentStatusItem]


class Author(VchasnoModel):
    """Comment author."""

    email: str | None = None
    name: str | None = None


class Comment(VchasnoModel):
    """Document comment."""

    id: str
    text: str | None = None
    document_id: str | None = None
    date_created: str | None = None
    email: str | None = None
    edrpou: str | None = None
    is_internal: bool | None = None
    type: str | None = None
    author: Author | None = None


class CommentList(VchasnoModel):
    """Paginated list of comments."""

    comments: list[Comment]
    next_cursor: str | None = None


class Review(VchasnoModel):
    """Review history entry."""

    user_email: str | None = None
    group_name: str | None = None
    is_last: bool | None = None
    action: str | None = None
    date_created: str | None = None


class ReviewRequest(VchasnoModel):
    """Review request entry."""

    user_from_email: str | None = None
    user_to_email: str | None = None
    group_to_name: str | None = None
    status: str | None = None
    date_created: str | None = None


class ReviewStatus(VchasnoModel):
    """Overall review status of a document."""

    status: str
    is_required: bool | None = None
    date_created: str | None = None
    date_updated: str | None = None


class FlowEntryInput(VchasnoModel):
    """Input model for set_flow() — typed alternative to dict."""

    edrpou: str
    emails: list[str] = Field(default_factory=list)
    order: int = 0
    sign_num: int = 1


class SignerEntityInput(VchasnoModel):
    """Input model for set_signers() — typed alternative to dict."""

    type: str
    id: str


class FlowEntry(VchasnoModel):
    """Multilateral document flow entry."""

    edrpou: str | None = None
    order: int | None = None
    pending_signatures: int | None = None
    emails: list[str] | None = None


class StructuredData(VchasnoModel):
    """Structured data from a document (flexible dict)."""

    details: dict[str, Any] | None = None
    parties_information: dict[str, Any] | None = None
    items: list[dict[str, Any]] | None = None
    total_price: dict[str, Any] | None = None


# Rebuild forward-ref for StampInfo used in SignatureDetail
SignatureDetail.model_rebuild()
