"""Delete requests endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno.models.common import UpdatedIds
from vchasno.models.documents import DeleteRequestRef


class AsyncDeleteRequests(AsyncEndpoint):
    """Asynchronous delete-requests endpoint group."""

    async def create(self, document_id: str, *, message: str) -> None:
        await self._request("POST", f"/api/v2/documents/{document_id}/delete-requests", json={"message": message})

    async def cancel(self, document_id: str) -> None:
        await self._request("DELETE", f"/api/v2/documents/{document_id}/delete-requests")

    async def accept(self, document_id: str) -> None:
        await self._request("POST", f"/api/v2/documents/{document_id}/delete-requests/acceptions")

    async def reject(self, document_id: str, *, reject_message: str) -> None:
        await self._request(
            "POST",
            f"/api/v2/documents/{document_id}/delete-requests/rejections",
            json={"reject_message": reject_message},
        )

    async def list(
        self,
        *,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        **extra: Any,
    ) -> list[DeleteRequestRef]:
        params = {
            k: v for k, v in {"status": status, "cursor": cursor, "limit": limit, **extra}.items() if v is not None
        }
        data = await self._request("GET", "/api/v2/documents/delete-requests", params=params or None)
        items = data if isinstance(data, list) else [data]
        return [DeleteRequestRef.model_validate(d) for d in items]

    async def lock_delete(self, document_ids: Sequence[str]) -> UpdatedIds:
        data = await self._request(
            "POST", "/api/v2/documents/delete-requests/lock-delete", json={"document_ids": list(document_ids)}
        )
        return UpdatedIds.model_validate(data)

    async def unlock_delete(self, document_ids: Sequence[str]) -> UpdatedIds:
        data = await self._request(
            "DELETE", "/api/v2/documents/delete-requests/lock-delete", json={"document_ids": list(document_ids)}
        )
        return UpdatedIds.model_validate(data)
