"""Archive models."""

from __future__ import annotations

from vchasno.models._base import VchasnoModel


class ArchiveDirectory(VchasnoModel):
    """An archive directory / folder."""

    id: int
    parent_id: int | None = None
    name: str
    date_created: str | None = None


class ArchiveDirectoryList(VchasnoModel):
    """Paginated list of archive directories."""

    directories: list[ArchiveDirectory]
    next_cursor: str | None = None


class ArchiveScanDocument(VchasnoModel):
    """A document created from an uploaded scan."""

    id: str | None = None
    title: str | None = None


class ArchiveScanResult(VchasnoModel):
    """Result of uploading scans."""

    documents: list[ArchiveScanDocument]


class ArchiveImportSignedResult(VchasnoModel):
    """Result of importing a signed document into the archive."""

    document_id: str
    signature_count: int
    counterparty_count: int
