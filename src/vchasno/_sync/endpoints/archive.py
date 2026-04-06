"""Archive endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import IO, Any, cast

from vchasno._files import open_file, open_files
from vchasno._sync._pagination import SyncCursorPage
from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.archive import (
    ArchiveDirectory,
    ArchiveImportSignedResult,
    ArchiveScanResult,
)


class SyncArchive(SyncEndpoint):
    """Asynchronous archive endpoint group."""

    def directories(
        self,
        *,
        parent_id: int | None = None,
        search: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> SyncCursorPage[ArchiveDirectory]:
        if limit is not None and not (1 <= limit <= 500):
            raise ValueError("limit must be between 1 and 500")
        params: dict[str, Any] = {}
        if parent_id is not None:
            params["parent_id"] = parent_id
        if search is not None:
            params["search"] = search
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        data = self._request("GET", "/api/v2/archive/directories", params=params or None)
        return SyncCursorPage._from_response(
            cast(dict[str, Any], data),
            model_cls=ArchiveDirectory,
            transport=self._t,
            path="/api/v2/archive/directories",
            params=params or {},
            data_key="directories",
        )

    def upload_scans(
        self, files: Sequence[str | Path | IO[bytes]], *, parent_id: int | None = None
    ) -> ArchiveScanResult:
        params: dict[str, Any] = {}
        if parent_id is not None:
            params["parent_id"] = parent_id
        with open_files(files, field_name="files", default_name="scan") as file_tuples:
            data = self._request("POST", "/api/v2/archive/scans", params=params or None, files=file_tuples)
        return ArchiveScanResult.model_validate(data)

    def import_signed_external(
        self,
        file: str | Path | IO[bytes],
        signatures: Sequence[str | Path | IO[bytes]],
        *,
        filename: str | None = None,
        **metadata: Any,
    ) -> ArchiveImportSignedResult:
        with (
            open_file(file, filename=filename, default_name="document") as (fname, fp),
            open_files(signatures, field_name="signatures", default_name="signature.p7s") as sig_tuples,
        ):
            file_tuples: list[Any] = [("file", (fname, fp)), *sig_tuples]
            data_fields: dict[str, str] = {}
            for k, v in metadata.items():
                if v is not None:
                    data_fields[k] = str(v)
            data = self._request(
                "POST", "/api/v2/archive/import-signed", files=file_tuples, data=data_fields or None
            )
        return ArchiveImportSignedResult.model_validate(data)

    def import_signed_internal(
        self,
        signed_file: str | Path | IO[bytes],
        *,
        filename: str | None = None,
        **metadata: Any,
    ) -> ArchiveImportSignedResult:
        with open_file(signed_file, filename=filename, default_name="signed_document") as (fname, fp):
            file_tuples: list[Any] = [("signed_file", (fname, fp))]
            data_fields: dict[str, str] = {}
            for k, v in metadata.items():
                if v is not None:
                    data_fields[k] = str(v)
            data = self._request(
                "POST", "/api/v2/archive/import-signed", files=file_tuples, data=data_fields or None
            )
        return ArchiveImportSignedResult.model_validate(data)
