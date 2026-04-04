"""Groups / teams endpoints."""

from __future__ import annotations

from typing import Any

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.groups import Group, GroupMember


class SyncGroups(SyncEndpoint):
    """Synchronous groups endpoint group."""

    def list(self) -> list[Group]:
        """GET /api/v2/groups."""
        data = self._request("GET", "/api/v2/groups")
        return [Group.model_validate(g) for g in data]

    def get(self, group_id: str) -> Group:
        """GET /api/v2/groups/{id}."""
        data = self._request("GET", f"/api/v2/groups/{group_id}")
        return Group.model_validate(data)

    def create(self, *, name: str) -> Group:
        """POST /api/v2/groups."""
        data = self._request("POST", "/api/v2/groups", json={"name": name})
        return Group.model_validate(data)

    def update(self, group_id: str, *, name: str) -> Group:
        """PATCH /api/v2/groups/{id}."""
        data = self._request("PATCH", f"/api/v2/groups/{group_id}", json={"name": name})
        return Group.model_validate(data)

    def delete(self, group_id: str) -> Any:
        """DELETE /api/v2/groups/{id}."""
        return self._request("DELETE", f"/api/v2/groups/{group_id}")

    def members(self, group_id: str) -> list[GroupMember]:
        """GET /api/v2/groups/{id}/members."""
        data = self._request("GET", f"/api/v2/groups/{group_id}/members")
        return [GroupMember.model_validate(m) for m in data]

    def add_members(self, group_id: str, *, role_ids: list[str]) -> list[GroupMember]:
        """POST /api/v2/groups/{id}/members."""
        data = self._request("POST", f"/api/v2/groups/{group_id}/members", json={"role_ids": role_ids})
        return [GroupMember.model_validate(m) for m in data]

    def remove_members(self, group_id: str, *, group_members: list[str]) -> Any:
        """POST /api/v2/groups/{id}/members/remove."""
        return self._request("POST", f"/api/v2/groups/{group_id}/members/remove", json={"group_members": group_members})


class AsyncGroups(AsyncEndpoint):
    """Asynchronous groups endpoint group."""

    async def list(self) -> list[Group]:
        data = await self._request("GET", "/api/v2/groups")
        return [Group.model_validate(g) for g in data]

    async def get(self, group_id: str) -> Group:
        data = await self._request("GET", f"/api/v2/groups/{group_id}")
        return Group.model_validate(data)

    async def create(self, *, name: str) -> Group:
        data = await self._request("POST", "/api/v2/groups", json={"name": name})
        return Group.model_validate(data)

    async def update(self, group_id: str, *, name: str) -> Group:
        data = await self._request("PATCH", f"/api/v2/groups/{group_id}", json={"name": name})
        return Group.model_validate(data)

    async def delete(self, group_id: str) -> Any:
        return await self._request("DELETE", f"/api/v2/groups/{group_id}")

    async def members(self, group_id: str) -> list[GroupMember]:
        data = await self._request("GET", f"/api/v2/groups/{group_id}/members")
        return [GroupMember.model_validate(m) for m in data]

    async def add_members(self, group_id: str, *, role_ids: list[str]) -> list[GroupMember]:
        data = await self._request("POST", f"/api/v2/groups/{group_id}/members", json={"role_ids": role_ids})
        return [GroupMember.model_validate(m) for m in data]

    async def remove_members(self, group_id: str, *, group_members: list[str]) -> Any:
        return await self._request("POST", f"/api/v2/groups/{group_id}/members/remove", json={"group_members": group_members})
