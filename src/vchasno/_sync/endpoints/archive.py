"""Archive endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import IO, Any

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.archive import (
    ArchiveDirectoryList,
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
    ) -> ArchiveDirectoryList:
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
        return ArchiveDirectoryList.model_validate(data)

    def upload_scans(
        self, files: Sequence[str | Path | IO[bytes]], *, parent_id: int | None = None
    ) -> ArchiveScanResult:
        params: dict[str, Any] = {}
        if parent_id is not None:
            params["parent_id"] = parent_id
        file_tuples: list[Any] = []
        opened: list[Any] = []
        for f in files:
            if isinstance(f, (str, Path)):
                p = Path(f)
                fp = open(p, "rb")
                opened.append(fp)
                file_tuples.append(("files", (p.name, fp)))
            else:
                file_tuples.append(("files", ("scan", f)))
        try:
            data = self._request("POST", "/api/v2/archive/scans", params=params or None, files=file_tuples)
        finally:
            for fp in opened:
                fp.close()
        return ArchiveScanResult.model_validate(data)

    def import_signed_external(
        self,
        file: str | Path | IO[bytes],
        signatures: Sequence[str | Path | IO[bytes]],
        *,
        filename: str | None = None,
        **metadata: Any,
    ) -> ArchiveImportSignedResult:
        opened: list[Any] = []
        if isinstance(file, (str, Path)):
            p = Path(file)
            fp = open(p, "rb")
            opened.append(fp)
            filename = filename or p.name
        else:
            fp = file
            filename = filename or "document"
        file_tuples: list[Any] = [("file", (filename, fp))]
        for sig in signatures:
            if isinstance(sig, (str, Path)):
                sp = Path(sig)
                sfp = open(sp, "rb")
                opened.append(sfp)
                file_tuples.append(("signatures", (sp.name, sfp)))
            else:
                file_tuples.append(("signatures", ("signature.p7s", sig)))
        data_fields: dict[str, str] = {}
        for k, v in metadata.items():
            if v is not None:
                data_fields[k] = str(v)
        try:
            data = self._request(
                "POST", "/api/v2/archive/import-signed", files=file_tuples, data=data_fields or None
            )
        finally:
            for f in opened:
                f.close()
        return ArchiveImportSignedResult.model_validate(data)

    def import_signed_internal(
        self,
        signed_file: str | Path | IO[bytes],
        *,
        filename: str | None = None,
        **metadata: Any,
    ) -> ArchiveImportSignedResult:
        opened: list[Any] = []
        if isinstance(signed_file, (str, Path)):
            p = Path(signed_file)
            fp = open(p, "rb")
            opened.append(fp)
            filename = filename or p.name
        else:
            fp = signed_file
            filename = filename or "signed_document"
        file_tuples: list[Any] = [("signed_file", (filename, fp))]
        data_fields: dict[str, str] = {}
        for k, v in metadata.items():
            if v is not None:
                data_fields[k] = str(v)
        try:
            data = self._request(
                "POST", "/api/v2/archive/import-signed", files=file_tuples, data=data_fields or None
            )
        finally:
            for f in opened:
                f.close()
        return ArchiveImportSignedResult.model_validate(data)
