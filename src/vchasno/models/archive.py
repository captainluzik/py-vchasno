"""Archive models."""

from __future__ import annotations

from pydantic import BaseModel


class ArchiveDirectory(BaseModel):
    """An archive directory / folder."""

    model_config = {"extra": "allow"}

    id: int
    parent_id: int | None = None
    name: str
    date_created: str | None = None


class ArchiveDirectoryList(BaseModel):
    """Paginated list of archive directories."""

    model_config = {"extra": "allow"}

    directories: list[ArchiveDirectory]
    next_cursor: str | None = None


class ArchiveScanDocument(BaseModel):
    """A document created from an uploaded scan."""

    id: str | None = None
    title: str | None = None

    model_config = {"extra": "allow"}


class ArchiveScanResult(BaseModel):
    """Result of uploading scans."""

    model_config = {"extra": "allow"}

    documents: list[ArchiveScanDocument]


class ArchiveImportSignedResult(BaseModel):
    """Result of importing a signed document into the archive."""

    model_config = {"extra": "allow"}

    document_id: str
    signature_count: int
    counterparty_count: int
