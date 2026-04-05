"""Child document endpoints."""

from __future__ import annotations

from typing import Any

from vchasno._async.endpoints._base import AsyncEndpoint


class AsyncChildren(AsyncEndpoint):
    """Asynchronous child documents endpoint group."""

    async def add(self, parent_id: str, child_id: str) -> Any:
        return await self._request("POST", f"/api/v2/documents/{parent_id}/child/{child_id}")

    async def remove(self, parent_id: str, child_id: str) -> Any:
        return await self._request("DELETE", f"/api/v2/documents/{parent_id}/child/{child_id}")
