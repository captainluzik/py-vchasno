"""Comments endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._sync._pagination import SyncCursorPage
from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno._utils import collect_params, validate_id
from vchasno.models.documents import Comment


class SyncComments(SyncEndpoint):
    """Asynchronous comments endpoint group."""

    def list(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        document_id: str | None = None,
        **extra: Any,
    ) -> SyncCursorPage[Comment]:
        params = collect_params(
            date_from=date_from,
            date_to=date_to,
            cursor=cursor,
            limit=limit,
            document_id=document_id,
            **extra,
        )
        data = self._request("GET", "/api/v2/documents/comments", params=params or None)
        return SyncCursorPage._from_response(
            cast(dict[str, Any], data),
            model_cls=Comment,
            transport=self._t,
            path="/api/v2/documents/comments",
            params=params or {},
            data_key="comments",
        )

    def list_for_document(self, document_id: str) -> list[Comment]:
        validate_id(document_id, "document_id")
        data = self._request("GET", f"/api/v2/documents/{document_id}/comments")
        if isinstance(data, dict) and "comments" in data:
            return [Comment.model_validate(c) for c in data["comments"]]
        return [Comment.model_validate(c) for c in cast(list[Any], data)]

    def add(self, document_id: str, *, text: str, is_internal: bool = False) -> None:
        validate_id(document_id, "document_id")
        self._request(
            "POST",
            f"/api/v2/documents/{document_id}/comments",
            json={"text": text, "is_internal": is_internal},
        )
