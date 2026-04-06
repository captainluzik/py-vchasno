"""Delete requests endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno._utils import collect_params, validate_id
from vchasno.models.common import UpdatedIds
from vchasno.models.documents import DeleteRequestRef
from vchasno.models.enums import DeleteRequestStatus


class SyncDeleteRequests(SyncEndpoint):
    """Asynchronous delete-requests endpoint group."""

    def create(self, document_id: str, *, message: str) -> None:
        validate_id(document_id, "document_id")
        self._request("POST", f"/api/v2/documents/{document_id}/delete-requests", json={"message": message})

    def cancel(self, document_id: str) -> None:
        validate_id(document_id, "document_id")
        self._request("DELETE", f"/api/v2/documents/{document_id}/delete-requests")

    def accept(self, document_id: str) -> None:
        validate_id(document_id, "document_id")
        self._request("POST", f"/api/v2/documents/{document_id}/delete-requests/acceptions")

    def reject(self, document_id: str, *, reject_message: str) -> None:
        validate_id(document_id, "document_id")
        self._request(
            "POST",
            f"/api/v2/documents/{document_id}/delete-requests/rejections",
            json={"reject_message": reject_message},
        )

    def list(
        self,
        *,
        status: str | DeleteRequestStatus | None = None,
        ids: list[str] | None = None,
        with_outgoing: bool | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        **extra: Any,
    ) -> list[DeleteRequestRef]:
        params = collect_params(
            status=status,
            with_outgoing=with_outgoing,
            cursor=cursor,
            limit=limit,
            **extra,
        )
        # Handle multi-value ids
        if ids:
            param_list = list(params.items()) if params else []
            param_list.extend(("ids", id_val) for id_val in ids)
            params = param_list
        data = self._request("GET", "/api/v2/documents/delete-requests", params=params or None)
        items = data if isinstance(data, list) else [data]
        return [DeleteRequestRef.model_validate(d) for d in items]

    def lock_delete(self, document_ids: Sequence[str]) -> UpdatedIds:
        data = self._request(
            "POST", "/api/v2/documents/delete-requests/lock-delete", json={"document_ids": list(document_ids)}
        )
        return UpdatedIds.model_validate(data)

    def unlock_delete(self, document_ids: Sequence[str]) -> UpdatedIds:
        data = self._request(
            "DELETE", "/api/v2/documents/delete-requests/lock-delete", json={"document_ids": list(document_ids)}
        )
        return UpdatedIds.model_validate(data)
