"""Document versions endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint


class SyncVersions(SyncEndpoint):
    """Synchronous versions endpoint group."""

    def upload(self, document_id: str, file: str | Path | BinaryIO, *, filename: str | None = None) -> Any:
        """POST /api/v2/documents/{id}/version."""
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
            return self._request("POST", f"/api/v2/documents/{document_id}/version", files=files)
        finally:
            if opened is not None:
                opened.close()

    def delete(self, document_id: str, version_id: str) -> Any:
        """DELETE /api/v2/documents/{id}/version/{version_id}."""
        return self._request("DELETE", f"/api/v2/documents/{document_id}/version/{version_id}")


class AsyncVersions(AsyncEndpoint):
    """Asynchronous versions endpoint group."""

    async def upload(self, document_id: str, file: str | Path | BinaryIO, *, filename: str | None = None) -> Any:
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
            return await self._request("POST", f"/api/v2/documents/{document_id}/version", files=files)
        finally:
            if opened is not None:
                opened.close()

    async def delete(self, document_id: str, version_id: str) -> Any:
        return await self._request("DELETE", f"/api/v2/documents/{document_id}/version/{version_id}")
