"""Tests for vchasno.endpoints.archive."""

from __future__ import annotations

import io
import tempfile
from unittest.mock import AsyncMock, MagicMock

import pytest

from vchasno._async._pagination import AsyncCursorPage
from vchasno._async.endpoints.archive import AsyncArchive
from vchasno._sync._pagination import SyncCursorPage
from vchasno._sync.endpoints.archive import SyncArchive
from vchasno.models.archive import ArchiveImportSignedResult, ArchiveScanResult

DIRS_DATA = {"directories": [{"id": 1, "name": "Dir"}], "next_cursor": None}
SCAN_DATA = {"documents": [{"id": "d1"}]}
IMPORT_DATA = {"document_id": "d1", "signature_count": 2, "counterparty_count": 1}


class TestSyncArchive:
    def _make(self):
        ep = SyncArchive(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_directories_no_params(self):
        ep, req = self._make()
        req.return_value = DIRS_DATA
        result = ep.directories()
        assert isinstance(result, SyncCursorPage)
        assert len(result.data) == 1
        assert result.directories == result.data
        req.assert_called_with("GET", "/api/v2/archive/directories", params=None)

    def test_directories_all_params(self):
        ep, req = self._make()
        req.return_value = DIRS_DATA
        ep.directories(parent_id=1, search="test", cursor="c", limit=10)
        req.assert_called_with(
            "GET", "/api/v2/archive/directories", params={"parent_id": 1, "search": "test", "cursor": "c", "limit": 10}
        )

    def test_upload_scans_binary_io(self):
        ep, req = self._make()
        req.return_value = SCAN_DATA
        buf = io.BytesIO(b"scan")
        result = ep.upload_scans([buf])
        assert isinstance(result, ArchiveScanResult)

    def test_upload_scans_path(self):
        ep, req = self._make()
        req.return_value = SCAN_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"data")
            f.flush()
            result = ep.upload_scans([f.name])
        assert isinstance(result, ArchiveScanResult)

    def test_upload_scans_with_parent_id(self):
        ep, req = self._make()
        req.return_value = SCAN_DATA
        buf = io.BytesIO(b"scan")
        ep.upload_scans([buf], parent_id=5)
        req.assert_called_once()
        call_kwargs = req.call_args
        assert call_kwargs.kwargs.get("params") == {"parent_id": 5}

    def test_upload_scans_no_parent_id(self):
        ep, req = self._make()
        req.return_value = SCAN_DATA
        buf = io.BytesIO(b"scan")
        ep.upload_scans([buf])
        call_kwargs = req.call_args
        assert call_kwargs.kwargs.get("params") is None

    def test_import_signed_external_binary_io(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"doc")
        sig = io.BytesIO(b"sig")
        result = ep.import_signed_external(doc, [sig])
        assert isinstance(result, ArchiveImportSignedResult)

    def test_import_signed_external_path(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"doc")
            f.flush()
            doc_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".p7s", delete=False) as f:
            f.write(b"sig")
            f.flush()
            sig_path = f.name
        result = ep.import_signed_external(doc_path, [sig_path])
        assert isinstance(result, ArchiveImportSignedResult)

    def test_import_signed_external_with_metadata(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"doc")
        sig = io.BytesIO(b"sig")
        ep.import_signed_external(doc, [sig], title="Doc Title", edrpou="12345678")
        call_kwargs = req.call_args
        data_arg = call_kwargs.kwargs.get("data")
        assert data_arg["title"] == "Doc Title"

    def test_import_signed_external_metadata_none_values(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"doc")
        sig = io.BytesIO(b"sig")
        ep.import_signed_external(doc, [sig], title=None)
        call_kwargs = req.call_args
        data_arg = call_kwargs.kwargs.get("data")
        assert data_arg is None  # None values are skipped, empty dict -> None

    def test_import_signed_external_custom_filename(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"doc")
        sig = io.BytesIO(b"sig")
        ep.import_signed_external(doc, [sig], filename="custom.pdf")
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files")
        assert files_arg[0][1][0] == "custom.pdf"

    def test_import_signed_internal_binary_io(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"signed")
        result = ep.import_signed_internal(doc)
        assert isinstance(result, ArchiveImportSignedResult)

    def test_import_signed_internal_path(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"doc")
            f.flush()
            result = ep.import_signed_internal(f.name)
        assert isinstance(result, ArchiveImportSignedResult)

    def test_import_signed_internal_with_metadata(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"signed")
        ep.import_signed_internal(doc, title="Title")
        call_kwargs = req.call_args
        data_arg = call_kwargs.kwargs.get("data")
        assert data_arg["title"] == "Title"

    def test_import_signed_internal_metadata_none(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"signed")
        ep.import_signed_internal(doc, title=None)
        call_kwargs = req.call_args
        data_arg = call_kwargs.kwargs.get("data")
        assert data_arg is None

    def test_import_signed_internal_custom_filename(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"signed")
        ep.import_signed_internal(doc, filename="signed.pdf")
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files")
        assert files_arg[0][1][0] == "signed.pdf"


class TestAsyncArchive:
    def _make(self):
        ep = AsyncArchive(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_directories_no_params(self):
        ep, req = self._make()
        req.return_value = DIRS_DATA
        result = await ep.directories()
        assert isinstance(result, AsyncCursorPage)
        assert len(result.data) == 1
        assert result.directories == result.data

    @pytest.mark.asyncio
    async def test_directories_all_params(self):
        ep, req = self._make()
        req.return_value = DIRS_DATA
        await ep.directories(parent_id=1, search="x", cursor="c", limit=10)

    @pytest.mark.asyncio
    async def test_upload_scans_binary_io(self):
        ep, req = self._make()
        req.return_value = SCAN_DATA
        buf = io.BytesIO(b"scan")
        result = await ep.upload_scans([buf])
        assert isinstance(result, ArchiveScanResult)

    @pytest.mark.asyncio
    async def test_upload_scans_path(self):
        ep, req = self._make()
        req.return_value = SCAN_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"data")
            f.flush()
            result = await ep.upload_scans([f.name])
        assert isinstance(result, ArchiveScanResult)

    @pytest.mark.asyncio
    async def test_upload_scans_with_parent_id(self):
        ep, req = self._make()
        req.return_value = SCAN_DATA
        buf = io.BytesIO(b"scan")
        await ep.upload_scans([buf], parent_id=5)

    @pytest.mark.asyncio
    async def test_upload_scans_no_parent_id(self):
        ep, req = self._make()
        req.return_value = SCAN_DATA
        buf = io.BytesIO(b"scan")
        await ep.upload_scans([buf])
        call_kwargs = req.call_args
        assert call_kwargs.kwargs.get("params") is None

    @pytest.mark.asyncio
    async def test_import_signed_external_binary_io(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"doc")
        sig = io.BytesIO(b"sig")
        result = await ep.import_signed_external(doc, [sig])
        assert isinstance(result, ArchiveImportSignedResult)

    @pytest.mark.asyncio
    async def test_import_signed_external_path(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"doc")
            f.flush()
            doc_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".p7s", delete=False) as f:
            f.write(b"sig")
            f.flush()
            sig_path = f.name
        result = await ep.import_signed_external(doc_path, [sig_path])
        assert isinstance(result, ArchiveImportSignedResult)

    @pytest.mark.asyncio
    async def test_import_signed_external_with_metadata(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"doc")
        sig = io.BytesIO(b"sig")
        await ep.import_signed_external(doc, [sig], title="T")

    @pytest.mark.asyncio
    async def test_import_signed_external_metadata_none(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"doc")
        sig = io.BytesIO(b"sig")
        await ep.import_signed_external(doc, [sig], title=None)

    @pytest.mark.asyncio
    async def test_import_signed_internal_binary_io(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"signed")
        result = await ep.import_signed_internal(doc)
        assert isinstance(result, ArchiveImportSignedResult)

    @pytest.mark.asyncio
    async def test_import_signed_internal_path(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"doc")
            f.flush()
            result = await ep.import_signed_internal(f.name)
        assert isinstance(result, ArchiveImportSignedResult)

    @pytest.mark.asyncio
    async def test_import_signed_internal_with_metadata(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"signed")
        await ep.import_signed_internal(doc, title="T")

    @pytest.mark.asyncio
    async def test_import_signed_internal_metadata_none(self):
        ep, req = self._make()
        req.return_value = IMPORT_DATA
        doc = io.BytesIO(b"signed")
        await ep.import_signed_internal(doc, title=None)
