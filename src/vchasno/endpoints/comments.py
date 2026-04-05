"""Comments endpoints."""

from __future__ import annotations

from typing import Any

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.documents import Comment, CommentList


class SyncComments(SyncEndpoint):
    """Synchronous comments endpoint group."""

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        document_id: str | None = None,
        **extra: Any,
    ) -> CommentList:
        """GET /api/v2/documents/comments."""
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
        """GET /api/v2/documents/{id}/comments."""
        data = self._request("GET", f"/api/v2/documents/{document_id}/comments")
        if isinstance(data, dict) and "comments" in data:
            return [Comment.model_validate(c) for c in data["comments"]]
        return [Comment.model_validate(c) for c in data]

    def add(self, document_id: str, *, text: str, is_internal: bool = False) -> Any:
        """POST /api/v2/documents/{id}/comments."""
        return self._request(
            "POST",
            f"/api/v2/documents/{document_id}/comments",
            json={"text": text, "is_internal": is_internal},
        )


class AsyncComments(AsyncEndpoint):
    """Asynchronous comments endpoint group."""

    async def list(
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
        data = await self._request("GET", "/api/v2/documents/comments", params=params or None)
        return CommentList.model_validate(data)

    async def list_for_document(self, document_id: str) -> list[Comment]:
        data = await self._request("GET", f"/api/v2/documents/{document_id}/comments")
        if isinstance(data, dict) and "comments" in data:
            return [Comment.model_validate(c) for c in data["comments"]]
        return [Comment.model_validate(c) for c in data]

    async def add(self, document_id: str, *, text: str, is_internal: bool = False) -> Any:
        return await self._request(
            "POST",
            f"/api/v2/documents/{document_id}/comments",
            json={"text": text, "is_internal": is_internal},
        )
