"""Reviews / approval endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.documents import Review, ReviewRequest, ReviewStatus


class SyncReviews(SyncEndpoint):
    """Asynchronous reviews endpoint group."""

    def history(self, document_id: str) -> list[Review]:
        data = self._request("GET", f"/api/v2/documents/{document_id}/reviews")
        return [Review.model_validate(r) for r in cast(list[Any], data)]

    def requests(self, document_id: str) -> list[ReviewRequest]:
        data = self._request("GET", f"/api/v2/documents/{document_id}/reviews/requests")
        return [ReviewRequest.model_validate(r) for r in cast(list[Any], data)]

    def status(self, document_id: str) -> ReviewStatus:
        data = self._request("GET", f"/api/v2/documents/{document_id}/reviews/status")
        return ReviewStatus.model_validate(data)

    def add_reviewer(
        self,
        document_id: str,
        *,
        user_to_email: str | None = None,
        group_to_name: str | None = None,
        is_parallel: bool = True,
    ) -> None:
        body: dict[str, Any] = {"is_parallel": is_parallel}
        if user_to_email is not None:
            body["user_to_email"] = user_to_email
        if group_to_name is not None:
            body["group_to_name"] = group_to_name
        self._request("POST", f"/api/v2/documents/{document_id}/reviews/requests", json=body)

    def remove_reviewer(
        self,
        document_id: str,
        *,
        user_to_email: str | None = None,
        group_to_name: str | None = None,
    ) -> None:
        body: dict[str, Any] = {}
        if user_to_email is not None:
            body["user_to_email"] = user_to_email
        if group_to_name is not None:
            body["group_to_name"] = group_to_name
        self._request("DELETE", f"/api/v2/documents/{document_id}/reviews/requests", json=body)
