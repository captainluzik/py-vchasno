"""Groups / teams endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno.models.groups import Group, GroupMember


class AsyncGroups(AsyncEndpoint):
    """Asynchronous groups endpoint group."""

    async def list(self) -> list[Group]:
        data = await self._request("GET", "/api/v2/groups")
        return [Group.model_validate(g) for g in cast(list[Any], data)]

    async def get(self, group_id: str) -> Group:
        data = await self._request("GET", f"/api/v2/groups/{group_id}")
        return Group.model_validate(data)

    async def create(self, *, name: str) -> Group:
        data = await self._request("POST", "/api/v2/groups", json={"name": name})
        return Group.model_validate(data)

    async def update(self, group_id: str, *, name: str) -> Group:
        data = await self._request("PATCH", f"/api/v2/groups/{group_id}", json={"name": name})
        return Group.model_validate(data)

    async def delete(self, group_id: str) -> None:
        await self._request("DELETE", f"/api/v2/groups/{group_id}")

    async def members(self, group_id: str) -> list[GroupMember]:
        data = await self._request("GET", f"/api/v2/groups/{group_id}/members")
        return [GroupMember.model_validate(m) for m in cast(list[Any], data)]

    async def add_members(self, group_id: str, *, role_ids: Sequence[str]) -> list[GroupMember]:
        data = await self._request("POST", f"/api/v2/groups/{group_id}/members", json={"role_ids": list(role_ids)})
        return [GroupMember.model_validate(m) for m in cast(list[Any], data)]

    async def remove_members(self, group_id: str, *, group_members: Sequence[str]) -> None:
        await self._request(
            "POST", f"/api/v2/groups/{group_id}/members/remove", json={"group_members": list(group_members)}
        )
