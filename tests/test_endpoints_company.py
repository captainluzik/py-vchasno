"""Tests for vchasno.endpoints.company."""

from __future__ import annotations

import io
import tempfile
from unittest.mock import AsyncMock, MagicMock

import pytest

from vchasno.endpoints.company import AsyncCompany, SyncCompany
from vchasno.models.common import CompanyCheck, CompanyCheckUpload


class TestSyncCompany:
    def _make(self):
        ep = SyncCompany(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_check(self):
        ep, req = self._make()
        req.return_value = {"edrpou": "12345678", "name": "Co", "is_registered": True}
        result = ep.check(edrpou="12345678")
        assert isinstance(result, CompanyCheck)

    def test_check_upload_binary_io(self):
        ep, req = self._make()
        req.return_value = {"companies": []}
        buf = io.BytesIO(b"csv")
        result = ep.check_upload(buf)
        assert isinstance(result, CompanyCheckUpload)

    def test_check_upload_binary_io_default_filename(self):
        ep, req = self._make()
        req.return_value = {"companies": []}
        buf = io.BytesIO(b"csv")
        ep.check_upload(buf)
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files") or call_kwargs[1].get("files")
        assert files_arg[0][1][0] == "companies"

    def test_check_upload_path(self):
        ep, req = self._make()
        req.return_value = {"companies": []}
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(b"data")
            f.flush()
            result = ep.check_upload(f.name)
        assert isinstance(result, CompanyCheckUpload)

    def test_check_upload_custom_filename(self):
        ep, req = self._make()
        req.return_value = {"companies": []}
        buf = io.BytesIO(b"csv")
        ep.check_upload(buf, filename="my.csv")
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files") or call_kwargs[1].get("files")
        assert files_arg[0][1][0] == "my.csv"


class TestAsyncCompany:
    def _make(self):
        ep = AsyncCompany(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_check(self):
        ep, req = self._make()
        req.return_value = {"edrpou": "12345678", "name": "Co", "is_registered": True}
        result = await ep.check(edrpou="12345678")
        assert isinstance(result, CompanyCheck)

    @pytest.mark.asyncio
    async def test_check_upload_binary_io(self):
        ep, req = self._make()
        req.return_value = {"companies": []}
        buf = io.BytesIO(b"csv")
        result = await ep.check_upload(buf)
        assert isinstance(result, CompanyCheckUpload)

    @pytest.mark.asyncio
    async def test_check_upload_path(self):
        ep, req = self._make()
        req.return_value = {"companies": []}
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(b"data")
            f.flush()
            result = await ep.check_upload(f.name)
        assert isinstance(result, CompanyCheckUpload)

    @pytest.mark.asyncio
    async def test_check_upload_default_filename(self):
        ep, req = self._make()
        req.return_value = {"companies": []}
        buf = io.BytesIO(b"csv")
        await ep.check_upload(buf)
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files") or call_kwargs[1].get("files")
        assert files_arg[0][1][0] == "companies"
