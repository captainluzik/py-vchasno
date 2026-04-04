"""Child document endpoints."""

from __future__ import annotations

from typing import Any

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint


class SyncChildren(SyncEndpoint):
    """Synchronous child documents endpoint group."""

    def add(self, parent_id: str, child_id: str) -> Any:
        """POST /api/v2/documents/{parent}/child/{child}."""
        return self._request("POST", f"/api/v2/documents/{parent_id}/child/{child_id}")

    def remove(self, parent_id: str, child_id: str) -> Any:
        """DELETE /api/v2/documents/{parent}/child/{child}."""
        return self._request("DELETE", f"/api/v2/documents/{parent_id}/child/{child_id}")


class AsyncChildren(AsyncEndpoint):
    """Asynchronous child documents endpoint group."""

    async def add(self, parent_id: str, child_id: str) -> Any:
        return await self._request("POST", f"/api/v2/documents/{parent_id}/child/{child_id}")

    async def remove(self, parent_id: str, child_id: str) -> Any:
        return await self._request("DELETE", f"/api/v2/documents/{parent_id}/child/{child_id}")
