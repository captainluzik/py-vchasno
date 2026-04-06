"""Child document endpoints."""

from __future__ import annotations

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno._utils import validate_id


class AsyncChildren(AsyncEndpoint):
    """Asynchronous child documents endpoint group."""

    async def add(self, parent_id: str, child_id: str) -> None:
        validate_id(parent_id, "parent_id")
        validate_id(child_id, "child_id")
        await self._request("POST", f"/api/v2/documents/{parent_id}/child/{child_id}")

    async def remove(self, parent_id: str, child_id: str) -> None:
        validate_id(parent_id, "parent_id")
        validate_id(child_id, "child_id")
        await self._request("DELETE", f"/api/v2/documents/{parent_id}/child/{child_id}")
