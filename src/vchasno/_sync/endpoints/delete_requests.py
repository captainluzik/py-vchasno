"""Delete requests endpoints."""

from __future__ import annotations

from typing import Any

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.common import UpdatedIds
from vchasno.models.documents import DeleteRequestRef


class SyncDeleteRequests(SyncEndpoint):
    """Asynchronous delete-requests endpoint group."""

    def create(self, document_id: str, *, message: str) -> None:
        self._request("POST", f"/api/v2/documents/{document_id}/delete-requests", json={"message": message})

    def cancel(self, document_id: str) -> None:
        self._request("DELETE", f"/api/v2/documents/{document_id}/delete-requests")

    def accept(self, document_id: str) -> None:
        self._request("POST", f"/api/v2/documents/{document_id}/delete-requests/acceptions")

    def reject(self, document_id: str, *, reject_message: str) -> None:
        self._request(
            "POST",
            f"/api/v2/documents/{document_id}/delete-requests/rejections",
            json={"reject_message": reject_message},
        )

    def list(
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
        data = self._request("GET", "/api/v2/documents/delete-requests", params=params or None)
        items = data if isinstance(data, list) else [data]
        return [DeleteRequestRef.model_validate(d) for d in items]

    def lock_delete(self, document_ids: list[str]) -> UpdatedIds:
        data = self._request(
            "POST", "/api/v2/documents/delete-requests/lock-delete", json={"document_ids": document_ids}
        )
        return UpdatedIds.model_validate(data)

    def unlock_delete(self, document_ids: list[str]) -> UpdatedIds:
        data = self._request(
            "DELETE", "/api/v2/documents/delete-requests/lock-delete", json={"document_ids": document_ids}
        )
        return UpdatedIds.model_validate(data)
