"""Document categories endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.common import DocumentCategoryInfo


class SyncCategories(SyncEndpoint):
    """Asynchronous categories endpoint group."""

    def list(self) -> list[DocumentCategoryInfo]:
        data = self._request("GET", "/api/v2/document-categories")
        return [DocumentCategoryInfo.model_validate(c) for c in cast(list[Any], data)]

    def create(self, *, title: str) -> None:
        self._request("POST", "/api/v2/document-categories", json={"title": title})

    def update(self, category_id: int, *, title: str) -> None:
        self._request("PATCH", f"/api/v2/document-categories/{category_id}", json={"title": title})

    def delete(self, category_id: int) -> None:
        self._request("DELETE", f"/api/v2/document-categories/{category_id}")
