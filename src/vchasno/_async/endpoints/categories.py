"""Document categories endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno.models.common import DocumentCategoryInfo


class AsyncCategories(AsyncEndpoint):
    """Asynchronous categories endpoint group."""

    async def list(self) -> list[DocumentCategoryInfo]:
        data = await self._request("GET", "/api/v2/document-categories")
        return [DocumentCategoryInfo.model_validate(c) for c in cast(list[Any], data)]

    async def create(self, *, title: str) -> None:
        await self._request("POST", "/api/v2/document-categories", json={"title": title})

    async def update(self, category_id: int, *, title: str) -> None:
        await self._request("PATCH", f"/api/v2/document-categories/{category_id}", json={"title": title})

    async def delete(self, category_id: int) -> None:
        await self._request("DELETE", f"/api/v2/document-categories/{category_id}")
