"""Tests for vchasno.endpoints.documents."""

from __future__ import annotations

import io
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from vchasno.endpoints.documents import AsyncDocuments, DocumentsMixin, SyncDocuments
from vchasno.models.documents import Document, DocumentList, DocumentStatusList, DownloadDocumentList, IncomingDocumentList
from vchasno.models.common import UpdatedIds


DOC_DATA = {"id": "d1", "status": 7000}
DOC_LIST_DATA = {"documents": [DOC_DATA], "next_cursor": None}
INCOMING_DOC_DATA = {"id": "i1", "status": 7000}
INCOMING_DOC_LIST_DATA = {"documents": [INCOMING_DOC_DATA], "next_cursor": None}


class TestDocumentsMixin:
    def test_list_params_filters_none(self):
        result = DocumentsMixin._list_params(a=1, b=None, c="x")
        assert result == {"a": 1, "c": "x"}

    def test_list_params_empty(self):
        result = DocumentsMixin._list_params()
        assert result == {}


class TestSyncDocuments:
    def _make(self) -> tuple[SyncDocuments, MagicMock]:
        transport = MagicMock()
        ep = SyncDocuments(transport)
        ep._request = MagicMock()
        return ep, ep._request

    def test_list(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        result = ep.list(status=7000)
        assert isinstance(result, DocumentList)
        req.assert_called_once_with("GET", "/api/v2/documents", params={"status": 7000})

    def test_get_wrapped(self):
        ep, req = self._make()
        req.return_value = {"documents": [DOC_DATA]}
        result = ep.get("d1")
        assert isinstance(result, Document)
        assert result.id == "d1"

    def test_get_unwrapped(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        result = ep.get("d1")
        assert isinstance(result, Document)

    def test_upload_with_binary_io(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        buf = io.BytesIO(b"content")
        result = ep.upload(buf)
        assert isinstance(result, DocumentList)

    def test_upload_with_binary_io_default_filename(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        buf = io.BytesIO(b"content")
        ep.upload(buf)
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files") or call_kwargs[1].get("files")
        assert files_arg[0][1][0] == "document"

    def test_upload_with_path(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"data")
            f.flush()
            result = ep.upload(f.name)
        assert isinstance(result, DocumentList)

    def test_upload_unwrapped_response(self):
        ep, req = self._make()
        req.return_value = DOC_DATA  # not wrapped
        buf = io.BytesIO(b"content")
        result = ep.upload(buf)
        assert isinstance(result, DocumentList)
        assert len(result.documents) == 1

    def test_upload_with_custom_filename(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        buf = io.BytesIO(b"content")
        ep.upload(buf, filename="custom.pdf")
        call_kwargs = req.call_args
        files_arg = call_kwargs.kwargs.get("files") or call_kwargs[1].get("files")
        assert files_arg[0][1][0] == "custom.pdf"

    def test_update_info(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        result = ep.update_info("d1", title="New Title")
        assert isinstance(result, Document)

    def test_update_recipient(self):
        ep, req = self._make()
        req.return_value = None
        ep.update_recipient("d1", edrpou="12345678", email="e@m.com")
        req.assert_called_once()

    def test_update_access_settings(self):
        ep, req = self._make()
        req.return_value = None
        ep.update_access_settings("d1", level="private")
        req.assert_called_once()

    def test_update_viewers_with_groups_and_roles(self):
        ep, req = self._make()
        req.return_value = None
        ep.update_viewers("d1", strategy="add", groups_ids=["g1"], roles_ids=["r1"])
        call_json = req.call_args.kwargs["json"]
        assert call_json["groups_ids"] == ["g1"]
        assert call_json["roles_ids"] == ["r1"]

    def test_update_viewers_without_optional(self):
        ep, req = self._make()
        req.return_value = None
        ep.update_viewers("d1", strategy="replace")
        call_json = req.call_args.kwargs["json"]
        assert "groups_ids" not in call_json
        assert "roles_ids" not in call_json

    def test_set_flow(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        result = ep.set_flow("d1", [{"edrpou": "e", "order": 1}])
        assert result == {"ok": True}

    def test_list_incoming(self):
        ep, req = self._make()
        req.return_value = INCOMING_DOC_LIST_DATA
        result = ep.list_incoming(status=7000)
        assert isinstance(result, IncomingDocumentList)

    def test_set_signers(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        result = ep.set_signers("d1", signer_entities=[{"email": "e@m.com"}], is_parallel=False)
        assert result == {"ok": True}

    def test_download_original_no_version(self):
        ep, req = self._make()
        req.return_value = b"bytes"
        result = ep.download_original("d1")
        assert result == b"bytes"
        req.assert_called_with("GET", "/api/v2/documents/d1/original", params=None)

    def test_download_original_with_version(self):
        ep, req = self._make()
        req.return_value = b"bytes"
        ep.download_original("d1", version="v1")
        req.assert_called_with("GET", "/api/v2/documents/d1/original", params={"version": "v1"})

    def test_download_archive(self):
        ep, req = self._make()
        req.return_value = b"zip"
        result = ep.download_archive("d1")
        assert result == b"zip"

    def test_download_p7s(self):
        ep, req = self._make()
        req.return_value = b"p7s"
        assert ep.download_p7s("d1") == b"p7s"

    def test_download_asic(self):
        ep, req = self._make()
        req.return_value = b"asic"
        assert ep.download_asic("d1") == b"asic"

    def test_download_documents(self):
        ep, req = self._make()
        req.return_value = {"documents": [{"id": "d1"}], "status": 200, "ready": True, "pending": False, "total": 1}
        result = ep.download_documents(["d1"])
        assert isinstance(result, DownloadDocumentList)

    def test_xml_to_pdf_create(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.xml_to_pdf_create("d1", force=True)
        req.assert_called_with("POST", "/api/v2/documents/d1/xml-to-pdf", json={"force": True})

    def test_xml_to_pdf_download(self):
        ep, req = self._make()
        req.return_value = b"pdf"
        assert ep.xml_to_pdf_download("d1") == b"pdf"

    def test_pdf_print(self):
        ep, req = self._make()
        req.return_value = b"pdf"
        assert ep.pdf_print("d1") == b"pdf"

    def test_statuses(self):
        ep, req = self._make()
        req.return_value = {"data_list": [{"document_id": "d1", "status_id": 7000, "status_text": "Uploaded"}]}
        result = ep.statuses(["d1"])
        assert isinstance(result, DocumentStatusList)

    def test_reject(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.reject("d1", text="reason")
        req.assert_called_with("POST", "/api/v2/documents/d1/reject", json={"text": "reason"})

    def test_send(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.send("d1")
        req.assert_called_with("POST", "/api/v2/documents/d1/send")

    def test_delete(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.delete("d1")
        req.assert_called_with("DELETE", "/api/v2/documents/d1")

    def test_archive_with_directory(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.archive(["d1"], directory_id="dir1")
        req.assert_called_with("POST", "/api/v2/documents/archive", json={"document_ids": ["d1"], "directory_id": "dir1"})

    def test_archive_without_directory(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.archive(["d1"])
        call_json = req.call_args.kwargs["json"]
        assert "directory_id" not in call_json

    def test_unarchive(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.unarchive(["d1"])
        req.assert_called_with("DELETE", "/api/v2/documents/archive", json={"document_ids": ["d1"]})

    def test_mark_as_processed(self):
        ep, req = self._make()
        req.return_value = {"updated_ids": ["d1"]}
        result = ep.mark_as_processed(["d1"])
        assert isinstance(result, UpdatedIds)

    def test_structured_data_download(self):
        ep, req = self._make()
        req.return_value = {"details": {}}
        result = ep.structured_data_download("d1", format="json")
        req.assert_called_with("GET", "/api/v2/documents/d1/structured-data/download", params={"format": "json"})


class TestAsyncDocuments:
    def _make(self) -> tuple[AsyncDocuments, AsyncMock]:
        transport = MagicMock()
        ep = AsyncDocuments(transport)
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_list(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        result = await ep.list(status=7000)
        assert isinstance(result, DocumentList)

    @pytest.mark.asyncio
    async def test_get_wrapped(self):
        ep, req = self._make()
        req.return_value = {"documents": [DOC_DATA]}
        result = await ep.get("d1")
        assert isinstance(result, Document)

    @pytest.mark.asyncio
    async def test_get_unwrapped(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        result = await ep.get("d1")
        assert isinstance(result, Document)

    @pytest.mark.asyncio
    async def test_upload_binary_io(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        buf = io.BytesIO(b"content")
        result = await ep.upload(buf)
        assert isinstance(result, DocumentList)

    @pytest.mark.asyncio
    async def test_upload_path(self):
        ep, req = self._make()
        req.return_value = DOC_LIST_DATA
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"data")
            f.flush()
            result = await ep.upload(f.name)
        assert isinstance(result, DocumentList)

    @pytest.mark.asyncio
    async def test_upload_unwrapped(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        buf = io.BytesIO(b"content")
        result = await ep.upload(buf)
        assert len(result.documents) == 1

    @pytest.mark.asyncio
    async def test_update_info(self):
        ep, req = self._make()
        req.return_value = DOC_DATA
        result = await ep.update_info("d1", title="T")
        assert isinstance(result, Document)

    @pytest.mark.asyncio
    async def test_update_recipient(self):
        ep, req = self._make()
        req.return_value = None
        await ep.update_recipient("d1", edrpou="e", email="e@m.com")

    @pytest.mark.asyncio
    async def test_update_access_settings(self):
        ep, req = self._make()
        req.return_value = None
        await ep.update_access_settings("d1", level="extended")

    @pytest.mark.asyncio
    async def test_update_viewers_with_groups_and_roles(self):
        ep, req = self._make()
        req.return_value = None
        await ep.update_viewers("d1", strategy="add", groups_ids=["g1"], roles_ids=["r1"])
        call_json = req.call_args.kwargs["json"]
        assert "groups_ids" in call_json

    @pytest.mark.asyncio
    async def test_update_viewers_without_optional(self):
        ep, req = self._make()
        req.return_value = None
        await ep.update_viewers("d1", strategy="replace")
        call_json = req.call_args.kwargs["json"]
        assert "groups_ids" not in call_json

    @pytest.mark.asyncio
    async def test_set_flow(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        result = await ep.set_flow("d1", [])
        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_list_incoming(self):
        ep, req = self._make()
        req.return_value = INCOMING_DOC_LIST_DATA
        result = await ep.list_incoming()
        assert isinstance(result, IncomingDocumentList)

    @pytest.mark.asyncio
    async def test_set_signers(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        await ep.set_signers("d1", signer_entities=[])

    @pytest.mark.asyncio
    async def test_download_original(self):
        ep, req = self._make()
        req.return_value = b"bytes"
        assert await ep.download_original("d1") == b"bytes"

    @pytest.mark.asyncio
    async def test_download_original_with_version(self):
        ep, req = self._make()
        req.return_value = b"bytes"
        await ep.download_original("d1", version="v1")
        req.assert_called_with("GET", "/api/v2/documents/d1/original", params={"version": "v1"})

    @pytest.mark.asyncio
    async def test_download_archive(self):
        ep, req = self._make()
        req.return_value = b"zip"
        assert await ep.download_archive("d1") == b"zip"

    @pytest.mark.asyncio
    async def test_download_p7s(self):
        ep, req = self._make()
        req.return_value = b"p7s"
        assert await ep.download_p7s("d1") == b"p7s"

    @pytest.mark.asyncio
    async def test_download_asic(self):
        ep, req = self._make()
        req.return_value = b"asic"
        assert await ep.download_asic("d1") == b"asic"

    @pytest.mark.asyncio
    async def test_download_documents(self):
        ep, req = self._make()
        req.return_value = {"documents": [{"id": "d1"}]}
        result = await ep.download_documents(["d1"])
        assert isinstance(result, DownloadDocumentList)

    @pytest.mark.asyncio
    async def test_xml_to_pdf_create(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.xml_to_pdf_create("d1")

    @pytest.mark.asyncio
    async def test_xml_to_pdf_download(self):
        ep, req = self._make()
        req.return_value = b"pdf"
        assert await ep.xml_to_pdf_download("d1") == b"pdf"

    @pytest.mark.asyncio
    async def test_pdf_print(self):
        ep, req = self._make()
        req.return_value = b"pdf"
        assert await ep.pdf_print("d1") == b"pdf"

    @pytest.mark.asyncio
    async def test_statuses(self):
        ep, req = self._make()
        req.return_value = {"data_list": []}
        result = await ep.statuses(["d1"])
        assert isinstance(result, DocumentStatusList)

    @pytest.mark.asyncio
    async def test_reject(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.reject("d1", text="reason")

    @pytest.mark.asyncio
    async def test_send(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.send("d1")

    @pytest.mark.asyncio
    async def test_delete(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.delete("d1")

    @pytest.mark.asyncio
    async def test_archive_with_directory(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.archive(["d1"], directory_id="dir1")
        call_json = req.call_args.kwargs["json"]
        assert call_json["directory_id"] == "dir1"

    @pytest.mark.asyncio
    async def test_archive_without_directory(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.archive(["d1"])
        call_json = req.call_args.kwargs["json"]
        assert "directory_id" not in call_json

    @pytest.mark.asyncio
    async def test_unarchive(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.unarchive(["d1"])

    @pytest.mark.asyncio
    async def test_mark_as_processed(self):
        ep, req = self._make()
        req.return_value = {"updated_ids": ["d1"]}
        result = await ep.mark_as_processed(["d1"])
        assert isinstance(result, UpdatedIds)

    @pytest.mark.asyncio
    async def test_structured_data_download(self):
        ep, req = self._make()
        req.return_value = {"details": {}}
        await ep.structured_data_download("d1")
