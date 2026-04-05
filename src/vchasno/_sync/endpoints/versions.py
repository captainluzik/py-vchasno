"""Document versions endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from vchasno._sync.endpoints._base import SyncEndpoint


class SyncVersions(SyncEndpoint):
    """Asynchronous versions endpoint group."""

    def upload(self, document_id: str, file: str | Path | BinaryIO, *, filename: str | None = None) -> None:
        opened: BinaryIO | None = None
        if isinstance(file, (str, Path)):
            path = Path(file)
            filename = filename or path.name
            opened = fp = open(path, "rb")
        else:
            fp = file
            filename = filename or "version"
        try:
            files = [("file", (filename, fp))]
            self._request("POST", f"/api/v2/documents/{document_id}/version", files=files)
        finally:
            if opened is not None:
                opened.close()

    def delete(self, document_id: str, version_id: str) -> None:
        self._request("DELETE", f"/api/v2/documents/{document_id}/version/{version_id}")
