"""Reviews / approval endpoints."""

from __future__ import annotations

from typing import Any

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno.models.documents import Review, ReviewRequest, ReviewStatus


class AsyncReviews(AsyncEndpoint):
    """Asynchronous reviews endpoint group."""

    async def history(self, document_id: str) -> list[Review]:
        data = await self._request("GET", f"/api/v2/documents/{document_id}/reviews")
        return [Review.model_validate(r) for r in data]

    async def requests(self, document_id: str) -> list[ReviewRequest]:
        data = await self._request("GET", f"/api/v2/documents/{document_id}/reviews/requests")
        return [ReviewRequest.model_validate(r) for r in data]

    async def status(self, document_id: str) -> ReviewStatus:
        data = await self._request("GET", f"/api/v2/documents/{document_id}/reviews/status")
        return ReviewStatus.model_validate(data)

    async def add_reviewer(
        self,
        document_id: str,
        *,
        user_to_email: str | None = None,
        group_to_name: str | None = None,
        is_parallel: bool = True,
    ) -> Any:
        body: dict[str, Any] = {"is_parallel": is_parallel}
        if user_to_email is not None:
            body["user_to_email"] = user_to_email
        if group_to_name is not None:
            body["group_to_name"] = group_to_name
        return await self._request("POST", f"/api/v2/documents/{document_id}/reviews/requests", json=body)

    async def remove_reviewer(
        self,
        document_id: str,
        *,
        user_to_email: str | None = None,
        group_to_name: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {}
        if user_to_email is not None:
            body["user_to_email"] = user_to_email
        if group_to_name is not None:
            body["group_to_name"] = group_to_name
        return await self._request("DELETE", f"/api/v2/documents/{document_id}/reviews/requests", json=body)
