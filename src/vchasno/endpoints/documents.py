"""Documents endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.documents import (
    Document,
    DocumentList,
    DocumentStatusList,
    DownloadDocumentList,
    IncomingDocumentList,
)
from vchasno.models.common import UpdatedIds


class DocumentsMixin:
    """Shared helpers for document endpoints."""

    @staticmethod
    def _list_params(**kwargs: Any) -> dict[str, Any]:
        return {k: v for k, v in kwargs.items() if v is not None}


class SyncDocuments(SyncEndpoint, DocumentsMixin):
    """Synchronous documents endpoint group."""

    def list(self, **filters: Any) -> DocumentList:
        """GET /api/v2/documents — list outgoing documents."""
        data = self._request("GET", "/api/v2/documents", params=self._list_params(**filters))
        return DocumentList.model_validate(data)

    def get(self, document_id: str, **filters: Any) -> Document:
        """GET /api/v2/documents/{id}."""
        data = self._request("GET", f"/api/v2/documents/{document_id}", params=self._list_params(**filters))
        # The single-document response may be wrapped in {"documents": [...]}
        if isinstance(data, dict) and "documents" in data:
            return Document.model_validate(data["documents"][0])
        return Document.model_validate(data)

    def upload(
        self,
        file: str | Path | BinaryIO,
        *,
        filename: str | None = None,
        **params: Any,
    ) -> DocumentList:
        """POST /api/v2/documents — upload a document (multipart)."""
        if isinstance(file, (str, Path)):
            path = Path(file)
            filename = filename or path.name
            fp = open(path, "rb")
            close = True
        else:
            fp = file
            filename = filename or "document"
            close = False
        try:
            files = [("file", (filename, fp))]
            query = self._list_params(**params)
            data = self._request("POST", "/api/v2/documents", params=query, files=files)
        finally:
            if close:
                fp.close()
        return DocumentList.model_validate(data) if isinstance(data, dict) and "documents" in data else DocumentList(documents=[Document.model_validate(data)])

    def update_info(self, document_id: str, **fields: Any) -> Document:
        """PATCH /api/v2/documents/{id}/info — edit document metadata."""
        data = self._request("PATCH", f"/api/v2/documents/{document_id}/info", json=fields)
        return Document.model_validate(data)

    def update_recipient(self, document_id: str, *, edrpou: str, email: str) -> None:
        """PATCH /api/v2/documents/{id}/recipient."""
        self._request("PATCH", f"/api/v2/documents/{document_id}/recipient", json={"edrpou": edrpou, "email": email})

    def update_access_settings(self, document_id: str, *, level: str) -> None:
        """PATCH /api/v2/documents/{id}/access-settings."""
        self._request("PATCH", f"/api/v2/documents/{document_id}/access-settings", json={"level": level})

    def update_viewers(self, document_id: str, *, strategy: str, groups_ids: list[str] | None = None, roles_ids: list[str] | None = None) -> None:
        """PATCH /api/v2/documents/{id}/viewers-settings."""
        body: dict[str, Any] = {"strategy": strategy}
        if groups_ids is not None:
            body["groups_ids"] = groups_ids
        if roles_ids is not None:
            body["roles_ids"] = roles_ids
        self._request("PATCH", f"/api/v2/documents/{document_id}/viewers-settings", json=body)

    def set_flow(self, document_id: str, flow: list[dict[str, Any]]) -> Any:
        """POST /api/v2/documents/{id}/flow — set multilateral signers."""
        return self._request("POST", f"/api/v2/documents/{document_id}/flow", json=flow)

    def list_incoming(self, **filters: Any) -> IncomingDocumentList:
        """GET /api/v2/incoming-documents."""
        data = self._request("GET", "/api/v2/incoming-documents", params=self._list_params(**filters))
        return IncomingDocumentList.model_validate(data)

    def set_signers(self, document_id: str, *, signer_entities: list[dict[str, str]], is_parallel: bool = True) -> Any:
        """POST /api/v2/documents/{id}/signers."""
        return self._request("POST", f"/api/v2/documents/{document_id}/signers", json={"signer_entities": signer_entities, "is_parallel": is_parallel})

    def download_original(self, document_id: str, *, version: str | None = None) -> bytes:
        """GET /api/v2/documents/{id}/original."""
        params = {"version": version} if version else None
        return self._request("GET", f"/api/v2/documents/{document_id}/original", params=params)

    def download_archive(self, document_id: str, **params: Any) -> bytes:
        """GET /api/v2/documents/{id}/archive."""
        return self._request("GET", f"/api/v2/documents/{document_id}/archive", params=self._list_params(**params))

    def download_p7s(self, document_id: str) -> bytes:
        """GET /api/v2/documents/{id}/p7s."""
        return self._request("GET", f"/api/v2/documents/{document_id}/p7s")

    def download_asic(self, document_id: str) -> bytes:
        """GET /api/v2/documents/{id}/asic."""
        return self._request("GET", f"/api/v2/documents/{document_id}/asic")

    def download_documents(self, ids: list[str]) -> DownloadDocumentList:
        """GET /api/v2/download-documents."""
        params = [("ids", i) for i in ids]
        data = self._request("GET", "/api/v2/download-documents", params=params)
        return DownloadDocumentList.model_validate(data)

    def xml_to_pdf_create(self, document_id: str, *, force: bool = False) -> Any:
        """POST /api/v2/documents/{id}/xml-to-pdf."""
        return self._request("POST", f"/api/v2/documents/{document_id}/xml-to-pdf", json={"force": force})

    def xml_to_pdf_download(self, document_id: str) -> bytes:
        """GET /api/v2/documents/{id}/xml-to-pdf."""
        return self._request("GET", f"/api/v2/documents/{document_id}/xml-to-pdf")

    def pdf_print(self, document_id: str) -> bytes:
        """GET /api/v2/documents/{id}/pdf/print."""
        return self._request("GET", f"/api/v2/documents/{document_id}/pdf/print")

    def statuses(self, document_ids: list[str]) -> DocumentStatusList:
        """POST /api/v2/documents/statuses."""
        data = self._request("POST", "/api/v2/documents/statuses", json={"document_ids": document_ids})
        return DocumentStatusList.model_validate(data)

    def reject(self, document_id: str, *, text: str) -> Any:
        """POST /api/v2/documents/{id}/reject."""
        return self._request("POST", f"/api/v2/documents/{document_id}/reject", json={"text": text})

    def send(self, document_id: str) -> Any:
        """POST /api/v2/documents/{id}/send."""
        return self._request("POST", f"/api/v2/documents/{document_id}/send")

    def delete(self, document_id: str) -> Any:
        """DELETE /api/v2/documents/{id}."""
        return self._request("DELETE", f"/api/v2/documents/{document_id}")

    def archive(self, document_ids: list[str], *, directory_id: str | None = None) -> Any:
        """POST /api/v2/documents/archive."""
        body: dict[str, Any] = {"document_ids": document_ids}
        if directory_id:
            body["directory_id"] = directory_id
        return self._request("POST", "/api/v2/documents/archive", json=body)

    def unarchive(self, document_ids: list[str]) -> Any:
        """DELETE /api/v2/documents/archive."""
        return self._request("DELETE", "/api/v2/documents/archive", json={"document_ids": document_ids})

    def mark_as_processed(self, document_ids: list[str]) -> UpdatedIds:
        """POST /api/v2/documents/mark-as-processed."""
        data = self._request("POST", "/api/v2/documents/mark-as-processed", json={"document_ids": document_ids})
        return UpdatedIds.model_validate(data)

    def structured_data_download(self, document_id: str, *, format: str = "json") -> Any:
        """GET /api/v2/documents/{id}/structured-data/download."""
        return self._request("GET", f"/api/v2/documents/{document_id}/structured-data/download", params={"format": format})


class AsyncDocuments(AsyncEndpoint, DocumentsMixin):
    """Asynchronous documents endpoint group."""

    async def list(self, **filters: Any) -> DocumentList:
        data = await self._request("GET", "/api/v2/documents", params=self._list_params(**filters))
        return DocumentList.model_validate(data)

    async def get(self, document_id: str, **filters: Any) -> Document:
        data = await self._request("GET", f"/api/v2/documents/{document_id}", params=self._list_params(**filters))
        if isinstance(data, dict) and "documents" in data:
            return Document.model_validate(data["documents"][0])
        return Document.model_validate(data)

    async def upload(
        self,
        file: str | Path | BinaryIO,
        *,
        filename: str | None = None,
        **params: Any,
    ) -> DocumentList:
        if isinstance(file, (str, Path)):
            path = Path(file)
            filename = filename or path.name
            fp = open(path, "rb")
            close = True
        else:
            fp = file
            filename = filename or "document"
            close = False
        try:
            files = [("file", (filename, fp))]
            query = self._list_params(**params)
            data = await self._request("POST", "/api/v2/documents", params=query, files=files)
        finally:
            if close:
                fp.close()
        return DocumentList.model_validate(data) if isinstance(data, dict) and "documents" in data else DocumentList(documents=[Document.model_validate(data)])

    async def update_info(self, document_id: str, **fields: Any) -> Document:
        data = await self._request("PATCH", f"/api/v2/documents/{document_id}/info", json=fields)
        return Document.model_validate(data)

    async def update_recipient(self, document_id: str, *, edrpou: str, email: str) -> None:
        await self._request("PATCH", f"/api/v2/documents/{document_id}/recipient", json={"edrpou": edrpou, "email": email})

    async def update_access_settings(self, document_id: str, *, level: str) -> None:
        await self._request("PATCH", f"/api/v2/documents/{document_id}/access-settings", json={"level": level})

    async def update_viewers(self, document_id: str, *, strategy: str, groups_ids: list[str] | None = None, roles_ids: list[str] | None = None) -> None:
        body: dict[str, Any] = {"strategy": strategy}
        if groups_ids is not None:
            body["groups_ids"] = groups_ids
        if roles_ids is not None:
            body["roles_ids"] = roles_ids
        await self._request("PATCH", f"/api/v2/documents/{document_id}/viewers-settings", json=body)

    async def set_flow(self, document_id: str, flow: list[dict[str, Any]]) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/flow", json=flow)

    async def list_incoming(self, **filters: Any) -> IncomingDocumentList:
        data = await self._request("GET", "/api/v2/incoming-documents", params=self._list_params(**filters))
        return IncomingDocumentList.model_validate(data)

    async def set_signers(self, document_id: str, *, signer_entities: list[dict[str, str]], is_parallel: bool = True) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/signers", json={"signer_entities": signer_entities, "is_parallel": is_parallel})

    async def download_original(self, document_id: str, *, version: str | None = None) -> bytes:
        params = {"version": version} if version else None
        return await self._request("GET", f"/api/v2/documents/{document_id}/original", params=params)

    async def download_archive(self, document_id: str, **params: Any) -> bytes:
        return await self._request("GET", f"/api/v2/documents/{document_id}/archive", params=self._list_params(**params))

    async def download_p7s(self, document_id: str) -> bytes:
        return await self._request("GET", f"/api/v2/documents/{document_id}/p7s")

    async def download_asic(self, document_id: str) -> bytes:
        return await self._request("GET", f"/api/v2/documents/{document_id}/asic")

    async def download_documents(self, ids: list[str]) -> DownloadDocumentList:
        params = [("ids", i) for i in ids]
        data = await self._request("GET", "/api/v2/download-documents", params=params)
        return DownloadDocumentList.model_validate(data)

    async def xml_to_pdf_create(self, document_id: str, *, force: bool = False) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/xml-to-pdf", json={"force": force})

    async def xml_to_pdf_download(self, document_id: str) -> bytes:
        return await self._request("GET", f"/api/v2/documents/{document_id}/xml-to-pdf")

    async def pdf_print(self, document_id: str) -> bytes:
        return await self._request("GET", f"/api/v2/documents/{document_id}/pdf/print")

    async def statuses(self, document_ids: list[str]) -> DocumentStatusList:
        data = await self._request("POST", "/api/v2/documents/statuses", json={"document_ids": document_ids})
        return DocumentStatusList.model_validate(data)

    async def reject(self, document_id: str, *, text: str) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/reject", json={"text": text})

    async def send(self, document_id: str) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/send")

    async def delete(self, document_id: str) -> Any:
        return await self._request("DELETE", f"/api/v2/documents/{document_id}")

    async def archive(self, document_ids: list[str], *, directory_id: str | None = None) -> Any:
        body: dict[str, Any] = {"document_ids": document_ids}
        if directory_id:
            body["directory_id"] = directory_id
        return await self._request("POST", "/api/v2/documents/archive", json=body)

    async def unarchive(self, document_ids: list[str]) -> Any:
        return await self._request("DELETE", "/api/v2/documents/archive", json={"document_ids": document_ids})

    async def mark_as_processed(self, document_ids: list[str]) -> UpdatedIds:
        data = await self._request("POST", "/api/v2/documents/mark-as-processed", json={"document_ids": document_ids})
        return UpdatedIds.model_validate(data)

    async def structured_data_download(self, document_id: str, *, format: str = "json") -> Any:
        return await self._request("GET", f"/api/v2/documents/{document_id}/structured-data/download", params={"format": format})
