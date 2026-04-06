"""Roles / employees endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno.models.roles import RoleList


class AsyncRoles(AsyncEndpoint):
    """Asynchronous roles endpoint group."""

    async def list(self) -> RoleList:
        data = await self._request("GET", "/api/v2/roles")
        return RoleList.model_validate(data)

    async def update(self, role_id: str, **settings: Any) -> None:
        await self._request("PATCH", f"/api/v2/roles/{role_id}", json=settings)

    async def delete(self, role_id: str) -> None:
        await self._request("DELETE", f"/api/v2/roles/{role_id}")

    async def invite_coworkers(self, *, emails: Sequence[str]) -> None:
        await self._request("POST", "/api/v2/invite/coworkers", json={"emails": list(emails)})

    async def create_coworker(
        self,
        *,
        email: str,
        first_name: str | None = None,
        second_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
    ) -> None:
        body: dict[str, Any] = {"email": email}
        if first_name is not None:
            body["first_name"] = first_name
        if second_name is not None:
            body["second_name"] = second_name
        if last_name is not None:
            body["last_name"] = last_name
        if phone is not None:
            body["phone"] = phone
        await self._request("POST", "/api/v2/coworker", json=body)

    async def create_tokens(self, *, emails: Sequence[str], expire_days: str | None = None) -> None:
        body: dict[str, Any] = {"emails": list(emails)}
        if expire_days is not None:
            body["expire_days"] = expire_days
        await self._request("POST", "/api/v2/tokens", json=body)

    async def delete_tokens(self, *, emails: Sequence[str]) -> None:
        await self._request("DELETE", "/api/v2/tokens", json={"emails": list(emails)})
