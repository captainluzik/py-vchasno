"""Child document endpoints."""

from __future__ import annotations

from typing import Any

from vchasno._sync.endpoints._base import SyncEndpoint


class SyncChildren(SyncEndpoint):
    """Asynchronous child documents endpoint group."""

    def add(self, parent_id: str, child_id: str) -> Any:
        return self._request("POST", f"/api/v2/documents/{parent_id}/child/{child_id}")

    def remove(self, parent_id: str, child_id: str) -> Any:
        return self._request("DELETE", f"/api/v2/documents/{parent_id}/child/{child_id}")
