"""Document versions endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import IO

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno._utils import validate_id


class AsyncVersions(AsyncEndpoint):
    """Asynchronous versions endpoint group."""

    async def upload(self, document_id: str, file: str | Path | IO[bytes], *, filename: str | None = None) -> None:
        validate_id(document_id, "document_id")
        opened: IO[bytes] | None = None
        if isinstance(file, (str, Path)):
            path = Path(file)
            filename = filename or path.name
            opened = fp = open(path, "rb")
        else:
            fp = file
            filename = filename or "version"
        try:
            files = [("file", (filename, fp))]
            await self._request("POST", f"/api/v2/documents/{document_id}/version", files=files)
        finally:
            if opened is not None:
                opened.close()

    async def delete(self, document_id: str, version_id: str) -> None:
        validate_id(document_id, "document_id")
        validate_id(version_id, "version_id")
        await self._request("DELETE", f"/api/v2/documents/{document_id}/version/{version_id}")
