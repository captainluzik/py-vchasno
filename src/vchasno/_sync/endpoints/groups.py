"""Groups / teams endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.groups import Group, GroupMember


class SyncGroups(SyncEndpoint):
    """Asynchronous groups endpoint group."""

    def list(self) -> list[Group]:
        data = self._request("GET", "/api/v2/groups")
        return [Group.model_validate(g) for g in cast(list[Any], data)]

    def get(self, group_id: str) -> Group:
        data = self._request("GET", f"/api/v2/groups/{group_id}")
        return Group.model_validate(data)

    def create(self, *, name: str) -> Group:
        data = self._request("POST", "/api/v2/groups", json={"name": name})
        return Group.model_validate(data)

    def update(self, group_id: str, *, name: str) -> Group:
        data = self._request("PATCH", f"/api/v2/groups/{group_id}", json={"name": name})
        return Group.model_validate(data)

    def delete(self, group_id: str) -> None:
        self._request("DELETE", f"/api/v2/groups/{group_id}")

    def members(self, group_id: str) -> list[GroupMember]:
        data = self._request("GET", f"/api/v2/groups/{group_id}/members")
        return [GroupMember.model_validate(m) for m in cast(list[Any], data)]

    def add_members(self, group_id: str, *, role_ids: list[str]) -> list[GroupMember]:
        data = self._request("POST", f"/api/v2/groups/{group_id}/members", json={"role_ids": role_ids})
        return [GroupMember.model_validate(m) for m in cast(list[Any], data)]

    def remove_members(self, group_id: str, *, group_members: list[str]) -> None:
        self._request("POST", f"/api/v2/groups/{group_id}/members/remove", json={"group_members": group_members})
