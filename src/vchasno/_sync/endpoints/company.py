"""Company check endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import IO

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.common import CompanyCheck, CompanyCheckUpload


class SyncCompany(SyncEndpoint):
    """Asynchronous company endpoint group."""

    def check(self, *, edrpou: str) -> CompanyCheck:
        data = self._request("POST", "/api/v2/check/company", json={"edrpou": edrpou})
        return CompanyCheck.model_validate(data)

    def check_upload(self, file: str | Path | IO[bytes], *, filename: str | None = None) -> CompanyCheckUpload:
        opened: IO[bytes] | None = None
        if isinstance(file, (str, Path)):
            p = Path(file)
            filename = filename or p.name
            opened = fp = open(p, "rb")
        else:
            fp = file
            filename = filename or "companies"
        try:
            files = [("file", (filename, fp))]
            data = self._request("POST", "/api/v2/check/company/upload", files=files)
        finally:
            if opened is not None:
                opened.close()
        return CompanyCheckUpload.model_validate(data)
