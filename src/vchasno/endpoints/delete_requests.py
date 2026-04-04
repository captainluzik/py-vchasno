"""Delete requests endpoints."""

from __future__ import annotations

from typing import Any

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.common import UpdatedIds


class SyncDeleteRequests(SyncEndpoint):
    """Synchronous delete-requests endpoint group."""

    def create(self, document_id: str, *, message: str) -> Any:
        """POST /api/v2/documents/{id}/delete-requests."""
        return self._request("POST", f"/api/v2/documents/{document_id}/delete-requests", json={"message": message})

    def cancel(self, document_id: str) -> Any:
        """DELETE /api/v2/documents/{id}/delete-requests."""
        return self._request("DELETE", f"/api/v2/documents/{document_id}/delete-requests")

    def accept(self, document_id: str) -> Any:
        """POST /api/v2/documents/{id}/delete-requests/acceptions."""
        return self._request("POST", f"/api/v2/documents/{document_id}/delete-requests/acceptions")

    def reject(self, document_id: str, *, reject_message: str) -> Any:
        """POST /api/v2/documents/{id}/delete-requests/rejections."""
        return self._request("POST", f"/api/v2/documents/{document_id}/delete-requests/rejections", json={"reject_message": reject_message})

    def list(self, **filters: Any) -> list[dict]:
        """GET /api/v2/documents/delete-requests."""
        params = {k: v for k, v in filters.items() if v is not None}
        data = self._request("GET", "/api/v2/documents/delete-requests", params=params)
        return data if isinstance(data, list) else [data]

    def lock_delete(self, document_ids: list[str]) -> UpdatedIds:
        """POST /api/v2/documents/delete-requests/lock-delete."""
        data = self._request("POST", "/api/v2/documents/delete-requests/lock-delete", json={"document_ids": document_ids})
        return UpdatedIds.model_validate(data)

    def unlock_delete(self, document_ids: list[str]) -> UpdatedIds:
        """DELETE /api/v2/documents/delete-requests/lock-delete."""
        data = self._request("DELETE", "/api/v2/documents/delete-requests/lock-delete", json={"document_ids": document_ids})
        return UpdatedIds.model_validate(data)


class AsyncDeleteRequests(AsyncEndpoint):
    """Asynchronous delete-requests endpoint group."""

    async def create(self, document_id: str, *, message: str) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/delete-requests", json={"message": message})

    async def cancel(self, document_id: str) -> Any:
        return await self._request("DELETE", f"/api/v2/documents/{document_id}/delete-requests")

    async def accept(self, document_id: str) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/delete-requests/acceptions")

    async def reject(self, document_id: str, *, reject_message: str) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/delete-requests/rejections", json={"reject_message": reject_message})

    async def list(self, **filters: Any) -> list[dict]:
        params = {k: v for k, v in filters.items() if v is not None}
        data = await self._request("GET", "/api/v2/documents/delete-requests", params=params)
        return data if isinstance(data, list) else [data]

    async def lock_delete(self, document_ids: list[str]) -> UpdatedIds:
        data = await self._request("POST", "/api/v2/documents/delete-requests/lock-delete", json={"document_ids": document_ids})
        return UpdatedIds.model_validate(data)

    async def unlock_delete(self, document_ids: list[str]) -> UpdatedIds:
        data = await self._request("DELETE", "/api/v2/documents/delete-requests/lock-delete", json={"document_ids": document_ids})
        return UpdatedIds.model_validate(data)
