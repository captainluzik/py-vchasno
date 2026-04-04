"""Archive models."""

from __future__ import annotations

from pydantic import BaseModel


class ArchiveDirectory(BaseModel):
    """An archive directory / folder."""

    id: int
    parent_id: int | None = None
    name: str
    date_created: str | None = None


class ArchiveDirectoryList(BaseModel):
    """Paginated list of archive directories."""

    directories: list[ArchiveDirectory]
    next_cursor: str | None = None


class ArchiveScanResult(BaseModel):
    """Result of uploading scans."""

    documents: list[dict]


class ArchiveImportSignedResult(BaseModel):
    """Result of importing a signed document into the archive."""

    document_id: str
    signature_count: int
    counterparty_count: int
