"""Document-related models."""

from __future__ import annotations

from pydantic import BaseModel


class Signature(BaseModel):
    """A document signature (short form from document list)."""

    id: str
    email: str | None = None
    date_created: str | None = None


class SignatureDetail(BaseModel):
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
    stamp: dict | None = None


class Recipient(BaseModel):
    """Recipient info."""

    edrpou: str | None = None
    emails: list[str] | None = None
    name: str | None = None
    is_emails_hidden: bool | None = None


class Version(BaseModel):
    """Document version."""

    id: str
    name: str | None = None
    role_id: str | None = None
    date_created: str | None = None
    is_sent: bool | None = None
    extension: str | None = None


class Document(BaseModel):
    """Outgoing document."""

    id: str
    vendor: str | None = None
    vendor_id: str | None = None
    status: int
    status_text: str | None = None
    signatures_to_finish: int | None = None
    first_sign_by: str | None = None
    extension: str | None = None
    signatures: list[Signature] | None = None
    title: str | None = None
    type: str | None = None
    amount: int | None = None
    date: str | None = None
    date_created: str | None = None
    date_finished: str | None = None
    date_delivered: str | None = None
    number: str | None = None
    preview_url: str | None = None
    url: str | None = None
    is_multilateral: bool | None = None
    category: int | None = None
    category_details: dict | None = None
    is_delivered: bool | None = None
    is_archived: bool | None = None
    is_internal: bool | None = None
    sd_status: str | None = None
    tags: list[dict] | None = None
    recipients: list[Recipient] | None = None
    fields: list[dict] | None = None
    versions: list[Version] | None = None
    parent: str | None = None
    children: list[str] | None = None
    delete_requests: list[dict] | None = None
    access_settings: dict | None = None


class DocumentList(BaseModel):
    """Paginated list of documents."""

    documents: list[Document]
    next_cursor: str | None = None


class IncomingDocument(BaseModel):
    """Incoming document."""

    id: str
    extension: str | None = None
    title: str | None = None
    type: str | None = None
    number: str | None = None
    status: int
    status_text: str | None = None
    edrpou_owner: str | None = None
    amount: int | None = None
    company_name: str | None = None
    signatures_to_finish: int | None = None
    first_sign_by: str | None = None
    date: str | None = None
    date_created: str | None = None
    date_delivered: str | None = None
    date_finished: str | None = None
    is_delivered: bool | None = None
    category: int | None = None
    category_details: dict | None = None
    signatures: list[Signature] | None = None
    preview_url: str | None = None
    url: str | None = None
    parent: str | None = None
    children: list[str] | None = None
    recipients: list[Recipient] | None = None
    fields: list[dict] | None = None
    versions: list[Version] | None = None
    is_multilateral: bool | None = None
    is_archived: bool | None = None
    sd_status: str | None = None
    tags: list[dict] | None = None
    delete_requests: list[dict] | None = None
    access_settings: dict | None = None


class IncomingDocumentList(BaseModel):
    """Paginated list of incoming documents."""

    documents: list[IncomingDocument]
    next_cursor: str | None = None


class DownloadDocument(BaseModel):
    """Download info for a document."""

    id: str
    extension: str | None = None
    archive_url: str | None = None
    original_url: str | None = None
    status: int | None = None
    xml_to_pdf_url: str | None = None


class DownloadDocumentList(BaseModel):
    """Response for download-documents endpoint."""

    status: int | None = None
    ready: bool | None = None
    pending: bool | None = None
    total: int | None = None
    documents: list[DownloadDocument]


class DocumentStatusItem(BaseModel):
    """Single item in the statuses response."""

    document_id: str
    status_id: int
    status_text: str


class DocumentStatusList(BaseModel):
    """Response for POST /documents/statuses."""

    data_list: list[DocumentStatusItem]


class Comment(BaseModel):
    """Document comment."""

    id: str
    text: str | None = None
    document_id: str | None = None
    date_created: str | None = None
    email: str | None = None
    edrpou: str | None = None
    is_internal: bool | None = None
    type: str | None = None
    author: dict | None = None


class CommentList(BaseModel):
    """Paginated list of comments."""

    comments: list[Comment]
    next_cursor: str | None = None


class Review(BaseModel):
    """Review history entry."""

    user_email: str | None = None
    group_name: str | None = None
    is_last: bool | None = None
    action: str | None = None
    date_created: str | None = None


class ReviewRequest(BaseModel):
    """Review request entry."""

    user_from_email: str | None = None
    user_to_email: str | None = None
    group_to_name: str | None = None
    status: str | None = None
    date_created: str | None = None


class ReviewStatus(BaseModel):
    """Overall review status of a document."""

    status: str
    is_required: bool | None = None
    date_created: str | None = None
    date_updated: str | None = None


class FlowEntry(BaseModel):
    """Multilateral document flow entry."""

    edrpou: str | None = None
    order: int | None = None
    pending_signatures: int | None = None
    emails: list[str] | None = None


class StructuredData(BaseModel):
    """Structured data from a document (flexible dict)."""

    details: dict | None = None
    parties_information: dict | None = None
    items: list[dict] | None = None
    total_price: dict | None = None
