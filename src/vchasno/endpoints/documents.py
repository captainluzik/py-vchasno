"""Documents endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.common import UpdatedIds
from vchasno.models.documents import (
    Document,
    DocumentList,
    DocumentStatusList,
    DownloadDocumentList,
    IncomingDocumentList,
)

_UNSET: Any = object()


def _collect(**kwargs: Any) -> dict[str, Any]:
    """Build a params dict dropping *_UNSET* and *None* values."""
    return {k: v for k, v in kwargs.items() if v is not _UNSET and v is not None}


class SyncDocuments(SyncEndpoint):
    """Synchronous documents endpoint group."""

    # -- list / get -----------------------------------------------------

    def list(
        self,
        *,
        status: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        category: int | None = None,
        edrpou: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        search: str | None = None,
        tag_id: str | None = None,
        is_archived: bool | None = None,
        sd_status: str | None = None,
        **extra: Any,
    ) -> DocumentList:
        """GET /api/v2/documents — list outgoing documents."""
        params = _collect(
            status=status,
            cursor=cursor,
            limit=limit,
            category=category,
            edrpou=edrpou,
            date_from=date_from,
            date_to=date_to,
            search=search,
            tag_id=tag_id,
            is_archived=is_archived,
            sd_status=sd_status,
            **extra,
        )
        data = self._request("GET", "/api/v2/documents", params=params or None)
        return DocumentList.model_validate(data)

    def get(self, document_id: str) -> Document:
        """GET /api/v2/documents/{id}."""
        data = self._request("GET", f"/api/v2/documents/{document_id}")
        # The single-document response may be wrapped in {"documents": [...]}
        if isinstance(data, dict) and "documents" in data:
            return Document.model_validate(data["documents"][0])
        return Document.model_validate(data)

    # -- upload / update ------------------------------------------------

    def upload(
        self,
        file: str | Path | BinaryIO,
        *,
        filename: str | None = None,
        category: int | None = None,
        edrpou: str | None = None,
        email: str | None = None,
        title: str | None = None,
        **extra: Any,
    ) -> DocumentList:
        """POST /api/v2/documents — upload a document (multipart)."""
        opened: BinaryIO | None = None
        if isinstance(file, (str, Path)):
            path = Path(file)
            filename = filename or path.name
            opened = fp = open(path, "rb")
        else:
            fp = file
            filename = filename or "document"
        try:
            files = [("file", (filename, fp))]
            query = _collect(
                category=category,
                edrpou=edrpou,
                email=email,
                title=title,
                **extra,
            )
            data = self._request("POST", "/api/v2/documents", params=query or None, files=files)
        finally:
            if opened is not None:
                opened.close()
        if isinstance(data, dict) and "documents" in data:
            return DocumentList.model_validate(data)
        return DocumentList(documents=[Document.model_validate(data)])

    def update_info(
        self,
        document_id: str,
        *,
        title: str = _UNSET,
        number: str = _UNSET,
        date: str = _UNSET,
        amount: int = _UNSET,
        category: int = _UNSET,
        first_sign_by: str = _UNSET,
        **extra: Any,
    ) -> Document:
        """PATCH /api/v2/documents/{id}/info — edit document metadata."""
        body = _collect(
            title=title,
            number=number,
            date=date,
            amount=amount,
            category=category,
            first_sign_by=first_sign_by,
            **extra,
        )
        data = self._request("PATCH", f"/api/v2/documents/{document_id}/info", json=body)
        return Document.model_validate(data)

    def update_recipient(self, document_id: str, *, edrpou: str, email: str) -> None:
        """PATCH /api/v2/documents/{id}/recipient."""
        self._request("PATCH", f"/api/v2/documents/{document_id}/recipient", json={"edrpou": edrpou, "email": email})

    def update_access_settings(self, document_id: str, *, level: str) -> None:
        """PATCH /api/v2/documents/{id}/access-settings."""
        self._request("PATCH", f"/api/v2/documents/{document_id}/access-settings", json={"level": level})

    def update_viewers(
        self,
        document_id: str,
        *,
        strategy: str,
        groups_ids: list[str] | None = None,
        roles_ids: list[str] | None = None,
    ) -> None:
        """PATCH /api/v2/documents/{id}/viewers-settings."""
        body: dict[str, Any] = {"strategy": strategy}
        if groups_ids is not None:
            body["groups_ids"] = groups_ids
        if roles_ids is not None:
            body["roles_ids"] = roles_ids
        self._request("PATCH", f"/api/v2/documents/{document_id}/viewers-settings", json=body)

    # -- flow / signers -------------------------------------------------

    def set_flow(self, document_id: str, flow: list[dict[str, Any]]) -> Any:
        """POST /api/v2/documents/{id}/flow — set multilateral signers."""
        return self._request("POST", f"/api/v2/documents/{document_id}/flow", json=flow)

    def set_signers(self, document_id: str, *, signer_entities: list[dict[str, str]], is_parallel: bool = True) -> Any:
        """POST /api/v2/documents/{id}/signers."""
        return self._request(
            "POST",
            f"/api/v2/documents/{document_id}/signers",
            json={"signer_entities": signer_entities, "is_parallel": is_parallel},
        )

    # -- incoming -------------------------------------------------------

    def list_incoming(
        self,
        *,
        status: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        category: int | None = None,
        edrpou: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        search: str | None = None,
        tag_id: str | None = None,
        is_archived: bool | None = None,
        sd_status: str | None = None,
        **extra: Any,
    ) -> IncomingDocumentList:
        """GET /api/v2/incoming-documents."""
        params = _collect(
            status=status,
            cursor=cursor,
            limit=limit,
            category=category,
            edrpou=edrpou,
            date_from=date_from,
            date_to=date_to,
            search=search,
            tag_id=tag_id,
            is_archived=is_archived,
            sd_status=sd_status,
            **extra,
        )
        data = self._request("GET", "/api/v2/incoming-documents", params=params or None)
        return IncomingDocumentList.model_validate(data)

    # -- downloads ------------------------------------------------------

    def download_original(self, document_id: str, *, version: str | None = None) -> bytes:
        """GET /api/v2/documents/{id}/original."""
        params = {"version": version} if version is not None else None
        return self._request("GET", f"/api/v2/documents/{document_id}/original", params=params)

    def download_archive(self, document_id: str) -> bytes:
        """GET /api/v2/documents/{id}/archive."""
        return self._request("GET", f"/api/v2/documents/{document_id}/archive")

    def download_p7s(self, document_id: str) -> bytes:
        """GET /api/v2/documents/{id}/p7s."""
        return self._request("GET", f"/api/v2/documents/{document_id}/p7s")

    def download_asic(self, document_id: str) -> bytes:
        """GET /api/v2/documents/{id}/asic."""
        return self._request("GET", f"/api/v2/documents/{document_id}/asic")

    def download_documents(self, ids: list[str]) -> DownloadDocumentList:
        """GET /api/v2/download-documents."""
        params = [("ids", i) for i in ids]  # type: ignore[attr-defined]
        data = self._request("GET", "/api/v2/download-documents", params=params)
        return DownloadDocumentList.model_validate(data)

    # -- conversion / print ---------------------------------------------

    def xml_to_pdf_create(self, document_id: str, *, force: bool = False) -> Any:
        """POST /api/v2/documents/{id}/xml-to-pdf."""
        return self._request("POST", f"/api/v2/documents/{document_id}/xml-to-pdf", json={"force": force})

    def xml_to_pdf_download(self, document_id: str) -> bytes:
        """GET /api/v2/documents/{id}/xml-to-pdf."""
        return self._request("GET", f"/api/v2/documents/{document_id}/xml-to-pdf")

    def pdf_print(self, document_id: str) -> bytes:
        """GET /api/v2/documents/{id}/pdf/print."""
        return self._request("GET", f"/api/v2/documents/{document_id}/pdf/print")

    # -- status / actions -----------------------------------------------

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
        if directory_id is not None:
            body["directory_id"] = directory_id
        return self._request("POST", "/api/v2/documents/archive", json=body)

    def unarchive(self, document_ids: list[str]) -> Any:
        """DELETE /api/v2/documents/archive."""
        return self._request("DELETE", "/api/v2/documents/archive", json={"document_ids": document_ids})

    def mark_as_processed(self, document_ids: list[str]) -> UpdatedIds:
        """POST /api/v2/documents/mark-as-processed."""
        data = self._request("POST", "/api/v2/documents/mark-as-processed", json={"document_ids": document_ids})
        return UpdatedIds.model_validate(data)

    def structured_data_download(self, document_id: str, *, output_format: str = "json") -> Any:
        """GET /api/v2/documents/{id}/structured-data/download."""
        return self._request(
            "GET", f"/api/v2/documents/{document_id}/structured-data/download", params={"format": output_format}
        )


# ---------------------------------------------------------------------------
# Async mirror
# ---------------------------------------------------------------------------


class AsyncDocuments(AsyncEndpoint):
    """Asynchronous documents endpoint group."""

    # -- list / get -----------------------------------------------------

    async def list(
        self,
        *,
        status: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        category: int | None = None,
        edrpou: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        search: str | None = None,
        tag_id: str | None = None,
        is_archived: bool | None = None,
        sd_status: str | None = None,
        **extra: Any,
    ) -> DocumentList:
        params = _collect(
            status=status,
            cursor=cursor,
            limit=limit,
            category=category,
            edrpou=edrpou,
            date_from=date_from,
            date_to=date_to,
            search=search,
            tag_id=tag_id,
            is_archived=is_archived,
            sd_status=sd_status,
            **extra,
        )
        data = await self._request("GET", "/api/v2/documents", params=params or None)
        return DocumentList.model_validate(data)

    async def get(self, document_id: str) -> Document:
        data = await self._request("GET", f"/api/v2/documents/{document_id}")
        if isinstance(data, dict) and "documents" in data:
            return Document.model_validate(data["documents"][0])
        return Document.model_validate(data)

    # -- upload / update ------------------------------------------------

    async def upload(
        self,
        file: str | Path | BinaryIO,
        *,
        filename: str | None = None,
        category: int | None = None,
        edrpou: str | None = None,
        email: str | None = None,
        title: str | None = None,
        **extra: Any,
    ) -> DocumentList:
        opened: BinaryIO | None = None
        if isinstance(file, (str, Path)):
            path = Path(file)
            filename = filename or path.name
            opened = fp = open(path, "rb")
        else:
            fp = file
            filename = filename or "document"
        try:
            files = [("file", (filename, fp))]
            query = _collect(
                category=category,
                edrpou=edrpou,
                email=email,
                title=title,
                **extra,
            )
            data = await self._request("POST", "/api/v2/documents", params=query or None, files=files)
        finally:
            if opened is not None:
                opened.close()
        if isinstance(data, dict) and "documents" in data:
            return DocumentList.model_validate(data)
        return DocumentList(documents=[Document.model_validate(data)])

    async def update_info(
        self,
        document_id: str,
        *,
        title: str = _UNSET,
        number: str = _UNSET,
        date: str = _UNSET,
        amount: int = _UNSET,
        category: int = _UNSET,
        first_sign_by: str = _UNSET,
        **extra: Any,
    ) -> Document:
        body = _collect(
            title=title,
            number=number,
            date=date,
            amount=amount,
            category=category,
            first_sign_by=first_sign_by,
            **extra,
        )
        data = await self._request("PATCH", f"/api/v2/documents/{document_id}/info", json=body)
        return Document.model_validate(data)

    async def update_recipient(self, document_id: str, *, edrpou: str, email: str) -> None:
        await self._request(
            "PATCH", f"/api/v2/documents/{document_id}/recipient", json={"edrpou": edrpou, "email": email}
        )

    async def update_access_settings(self, document_id: str, *, level: str) -> None:
        await self._request("PATCH", f"/api/v2/documents/{document_id}/access-settings", json={"level": level})

    async def update_viewers(
        self,
        document_id: str,
        *,
        strategy: str,
        groups_ids: list[str] | None = None,
        roles_ids: list[str] | None = None,
    ) -> None:
        body: dict[str, Any] = {"strategy": strategy}
        if groups_ids is not None:
            body["groups_ids"] = groups_ids
        if roles_ids is not None:
            body["roles_ids"] = roles_ids
        await self._request("PATCH", f"/api/v2/documents/{document_id}/viewers-settings", json=body)

    # -- flow / signers -------------------------------------------------

    async def set_flow(self, document_id: str, flow: list[dict[str, Any]]) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/flow", json=flow)

    async def set_signers(
        self, document_id: str, *, signer_entities: list[dict[str, str]], is_parallel: bool = True
    ) -> Any:
        return await self._request(
            "POST",
            f"/api/v2/documents/{document_id}/signers",
            json={"signer_entities": signer_entities, "is_parallel": is_parallel},
        )

    # -- incoming -------------------------------------------------------

    async def list_incoming(
        self,
        *,
        status: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        category: int | None = None,
        edrpou: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        search: str | None = None,
        tag_id: str | None = None,
        is_archived: bool | None = None,
        sd_status: str | None = None,
        **extra: Any,
    ) -> IncomingDocumentList:
        params = _collect(
            status=status,
            cursor=cursor,
            limit=limit,
            category=category,
            edrpou=edrpou,
            date_from=date_from,
            date_to=date_to,
            search=search,
            tag_id=tag_id,
            is_archived=is_archived,
            sd_status=sd_status,
            **extra,
        )
        data = await self._request("GET", "/api/v2/incoming-documents", params=params or None)
        return IncomingDocumentList.model_validate(data)

    # -- downloads ------------------------------------------------------

    async def download_original(self, document_id: str, *, version: str | None = None) -> bytes:
        params = {"version": version} if version is not None else None
        return await self._request("GET", f"/api/v2/documents/{document_id}/original", params=params)

    async def download_archive(self, document_id: str) -> bytes:
        return await self._request("GET", f"/api/v2/documents/{document_id}/archive")

    async def download_p7s(self, document_id: str) -> bytes:
        return await self._request("GET", f"/api/v2/documents/{document_id}/p7s")

    async def download_asic(self, document_id: str) -> bytes:
        return await self._request("GET", f"/api/v2/documents/{document_id}/asic")

    async def download_documents(self, ids: list[str]) -> DownloadDocumentList:
        params = [("ids", i) for i in ids]  # type: ignore[attr-defined]
        data = await self._request("GET", "/api/v2/download-documents", params=params)
        return DownloadDocumentList.model_validate(data)

    # -- conversion / print ---------------------------------------------

    async def xml_to_pdf_create(self, document_id: str, *, force: bool = False) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/xml-to-pdf", json={"force": force})

    async def xml_to_pdf_download(self, document_id: str) -> bytes:
        return await self._request("GET", f"/api/v2/documents/{document_id}/xml-to-pdf")

    async def pdf_print(self, document_id: str) -> bytes:
        return await self._request("GET", f"/api/v2/documents/{document_id}/pdf/print")

    # -- status / actions -----------------------------------------------

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
        if directory_id is not None:
            body["directory_id"] = directory_id
        return await self._request("POST", "/api/v2/documents/archive", json=body)

    async def unarchive(self, document_ids: list[str]) -> Any:
        return await self._request("DELETE", "/api/v2/documents/archive", json={"document_ids": document_ids})

    async def mark_as_processed(self, document_ids: list[str]) -> UpdatedIds:
        data = await self._request("POST", "/api/v2/documents/mark-as-processed", json={"document_ids": document_ids})
        return UpdatedIds.model_validate(data)

    async def structured_data_download(self, document_id: str, *, output_format: str = "json") -> Any:
        return await self._request(
            "GET", f"/api/v2/documents/{document_id}/structured-data/download", params={"format": output_format}
        )
