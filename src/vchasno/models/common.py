"""Shared / common models."""

from __future__ import annotations

from vchasno.models._base import VchasnoModel


class DocumentCategoryInfo(VchasnoModel):
    """Document category details returned by GET /api/v2/document-categories."""

    category_id: int
    category_title: str
    is_public: bool
    date_updated: str | None = None
    date_created: str | None = None


class CustomField(VchasnoModel):
    """A custom field definition."""

    id: str
    name: str
    type: str
    order: int | None = None
    company_id: str | None = None
    is_required: bool | None = None
    created_by: str | None = None


class DocumentField(VchasnoModel):
    """A custom field value attached to a document."""

    field_id: str
    name: str
    type: str
    is_required: bool
    value: str | None = None
    date_updated: str | None = None
    date_created: str | None = None


class ReviewSettings(VchasnoModel):
    """Review configuration within a template."""


class SignersSettings(VchasnoModel):
    """Signers configuration within a template."""


class ViewersSettings(VchasnoModel):
    """Viewers configuration within a template."""


class FieldsSettings(VchasnoModel):
    """Fields configuration within a template."""


class TagsSettings(VchasnoModel):
    """Tags configuration within a template."""


class Template(VchasnoModel):
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


class ReportRequest(VchasnoModel):
    """Result of requesting a report."""

    report_id: str


class ReportStatus(VchasnoModel):
    """Report readiness status."""

    status: str
    filename: str | None = None


class CompanyCheck(VchasnoModel):
    """Company registration check result."""

    edrpou: str
    name: str
    is_registered: bool


class CompanyCheckUpload(VchasnoModel):
    """Bulk company check result."""

    companies: list[CompanyCheck]
    percentage: str | None = None
    invalid_row_numbers: list[str] | None = None
    rows_invalid: str | None = None
    rows_total: str | None = None


class UpdatedIds(VchasnoModel):
    """Generic response with a list of updated IDs."""

    updated_ids: list[str]


class ActionResult(VchasnoModel):
    """Generic successful action response (for endpoints with unstructured success bodies)."""
