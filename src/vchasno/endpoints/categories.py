"""Document categories endpoints."""

from __future__ import annotations

from typing import Any

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.common import DocumentCategoryInfo


class SyncCategories(SyncEndpoint):
    """Synchronous categories endpoint group."""

    def list(self) -> list[DocumentCategoryInfo]:
        """GET /api/v2/document-categories."""
        data = self._request("GET", "/api/v2/document-categories")
        return [DocumentCategoryInfo.model_validate(c) for c in data]

    def create(self, *, title: str) -> Any:
        """POST /api/v2/document-categories."""
        return self._request("POST", "/api/v2/document-categories", json={"title": title})

    def update(self, category_id: int, *, title: str) -> Any:
        """PATCH /api/v2/document-categories/{id}."""
        return self._request("PATCH", f"/api/v2/document-categories/{category_id}", json={"title": title})

    def delete(self, category_id: int) -> Any:
        """DELETE /api/v2/document-categories/{id}."""
        return self._request("DELETE", f"/api/v2/document-categories/{category_id}")


class AsyncCategories(AsyncEndpoint):
    """Asynchronous categories endpoint group."""

    async def list(self) -> list[DocumentCategoryInfo]:
        data = await self._request("GET", "/api/v2/document-categories")
        return [DocumentCategoryInfo.model_validate(c) for c in data]

    async def create(self, *, title: str) -> Any:
        return await self._request("POST", "/api/v2/document-categories", json={"title": title})

    async def update(self, category_id: int, *, title: str) -> Any:
        return await self._request("PATCH", f"/api/v2/document-categories/{category_id}", json={"title": title})

    async def delete(self, category_id: int) -> Any:
        return await self._request("DELETE", f"/api/v2/document-categories/{category_id}")
