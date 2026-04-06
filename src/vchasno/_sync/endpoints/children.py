"""Child document endpoints."""

from __future__ import annotations

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno._utils import validate_id


class SyncChildren(SyncEndpoint):
    """Asynchronous child documents endpoint group."""

    def add(self, parent_id: str, child_id: str) -> None:
        validate_id(parent_id, "parent_id")
        validate_id(child_id, "child_id")
        self._request("POST", f"/api/v2/documents/{parent_id}/child/{child_id}")

    def remove(self, parent_id: str, child_id: str) -> None:
        validate_id(parent_id, "parent_id")
        validate_id(child_id, "child_id")
        self._request("DELETE", f"/api/v2/documents/{parent_id}/child/{child_id}")
