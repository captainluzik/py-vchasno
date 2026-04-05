"""Shared / common models."""

from __future__ import annotations

from pydantic import BaseModel


class DocumentCategoryInfo(BaseModel):
    """Document category details returned by GET /api/v2/document-categories."""

    category_id: int
    category_title: str
    is_public: bool
    date_updated: str | None = None
    date_created: str | None = None


class CustomField(BaseModel):
    """A custom field definition."""

    id: str
    name: str
    type: str
    order: int | None = None
    company_id: str | None = None
    is_required: bool | None = None
    created_by: str | None = None


class DocumentField(BaseModel):
    """A custom field value attached to a document."""

    field_id: str
    name: str
    type: str
    is_required: bool
    value: str | None = None
    date_updated: str | None = None
    date_created: str | None = None


class ReviewSettings(BaseModel):
    """Review configuration within a template."""

    model_config = {"extra": "allow"}


class SignersSettings(BaseModel):
    """Signers configuration within a template."""

    model_config = {"extra": "allow"}


class ViewersSettings(BaseModel):
    """Viewers configuration within a template."""

    model_config = {"extra": "allow"}


class FieldsSettings(BaseModel):
    """Fields configuration within a template."""

    model_config = {"extra": "allow"}


class TagsSettings(BaseModel):
    """Tags configuration within a template."""

    model_config = {"extra": "allow"}


class Template(BaseModel):
    """Scenario / template."""

    id: str
    name: str
    review_settings: ReviewSettings | None = None
    signers_settings: SignersSettings | None = None
    viewers_settings: ViewersSettings | None = None
    fields_settings: FieldsSettings | None = None
    tags_settings: TagsSettings | None = None
    created_by: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class ReportRequest(BaseModel):
    """Result of requesting a report."""

    report_id: str


class ReportStatus(BaseModel):
    """Report readiness status."""

    status: str
    filename: str | None = None


class CompanyCheck(BaseModel):
    """Company registration check result."""

    edrpou: str
    name: str
    is_registered: bool


class CompanyCheckUpload(BaseModel):
    """Bulk company check result."""

    companies: list[CompanyCheck]
    percentage: str | None = None
    invalid_row_numbers: list[str] | None = None
    rows_invalid: str | None = None
    rows_total: str | None = None


class UpdatedIds(BaseModel):
    """Generic response with a list of updated IDs."""

    updated_ids: list[str]
