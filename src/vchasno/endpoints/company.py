"""Company check endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.common import CompanyCheck, CompanyCheckUpload


class SyncCompany(SyncEndpoint):
    """Synchronous company endpoint group."""

    def check(self, *, edrpou: str) -> CompanyCheck:
        """POST /api/v2/check/company."""
        data = self._request("POST", "/api/v2/check/company", json={"edrpou": edrpou})
        return CompanyCheck.model_validate(data)

    def check_upload(self, file: str | Path | BinaryIO, *, filename: str | None = None) -> CompanyCheckUpload:
        """POST /api/v2/check/company/upload."""
        if isinstance(file, (str, Path)):
            p = Path(file)
            fp = open(p, "rb")
            filename = filename or p.name
            close = True
        else:
            fp = file
            filename = filename or "companies"
            close = False
        try:
            files = [("file", (filename, fp))]
            data = self._request("POST", "/api/v2/check/company/upload", files=files)
        finally:
            if close:
                fp.close()
        return CompanyCheckUpload.model_validate(data)


class AsyncCompany(AsyncEndpoint):
    """Asynchronous company endpoint group."""

    async def check(self, *, edrpou: str) -> CompanyCheck:
        data = await self._request("POST", "/api/v2/check/company", json={"edrpou": edrpou})
        return CompanyCheck.model_validate(data)

    async def check_upload(self, file: str | Path | BinaryIO, *, filename: str | None = None) -> CompanyCheckUpload:
        if isinstance(file, (str, Path)):
            p = Path(file)
            fp = open(p, "rb")
            filename = filename or p.name
            close = True
        else:
            fp = file
            filename = filename or "companies"
            close = False
        try:
            files = [("file", (filename, fp))]
            data = await self._request("POST", "/api/v2/check/company/upload", files=files)
        finally:
            if close:
                fp.close()
        return CompanyCheckUpload.model_validate(data)
