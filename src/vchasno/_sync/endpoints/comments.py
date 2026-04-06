"""Comments endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.documents import Comment, CommentList


class SyncComments(SyncEndpoint):
    """Asynchronous comments endpoint group."""

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        document_id: str | None = None,
        **extra: Any,
    ) -> CommentList:
        params = {
            k: v
            for k, v in {
                "cursor": cursor,
                "limit": limit,
                "document_id": document_id,
                **extra,
            }.items()
            if v is not None
        }
        data = self._request("GET", "/api/v2/documents/comments", params=params or None)
        return CommentList.model_validate(data)

    def list_for_document(self, document_id: str) -> list[Comment]:
        data = self._request("GET", f"/api/v2/documents/{document_id}/comments")
        if isinstance(data, dict) and "comments" in data:
            return [Comment.model_validate(c) for c in data["comments"]]
        return [Comment.model_validate(c) for c in cast(list[Any], data)]

    def add(self, document_id: str, *, text: str, is_internal: bool = False) -> None:
        self._request(
            "POST",
            f"/api/v2/documents/{document_id}/comments",
            json={"text": text, "is_internal": is_internal},
        )
