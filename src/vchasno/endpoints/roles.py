"""Roles / employees endpoints."""

from __future__ import annotations

from typing import Any

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.roles import Role, RoleList


class SyncRoles(SyncEndpoint):
    """Synchronous roles endpoint group."""

    def list(self) -> RoleList:
        """GET /api/v2/roles."""
        data = self._request("GET", "/api/v2/roles")
        return RoleList.model_validate(data)

    def update(self, role_id: str, **settings: Any) -> Any:
        """PATCH /api/v2/roles/{id}."""
        return self._request("PATCH", f"/api/v2/roles/{role_id}", json=settings)

    def delete(self, role_id: str) -> Any:
        """DELETE /api/v2/roles/{id}."""
        return self._request("DELETE", f"/api/v2/roles/{role_id}")

    def invite_coworkers(self, *, emails: list[str]) -> Any:
        """POST /api/v2/invite/coworkers."""
        return self._request("POST", "/api/v2/invite/coworkers", json={"emails": emails})

    def create_coworker(self, *, email: str, first_name: str | None = None, second_name: str | None = None, last_name: str | None = None, phone: str | None = None) -> Any:
        """POST /api/v2/coworker."""
        body: dict[str, Any] = {"email": email}
        if first_name:
            body["first_name"] = first_name
        if second_name:
            body["second_name"] = second_name
        if last_name:
            body["last_name"] = last_name
        if phone:
            body["phone"] = phone
        return self._request("POST", "/api/v2/coworker", json=body)

    def create_tokens(self, *, emails: list[str], expire_days: str | None = None) -> Any:
        """POST /api/v2/tokens."""
        body: dict[str, Any] = {"emails": emails}
        if expire_days:
            body["expire_days"] = expire_days
        return self._request("POST", "/api/v2/tokens", json=body)

    def delete_tokens(self, *, emails: list[str]) -> Any:
        """DELETE /api/v2/tokens."""
        return self._request("DELETE", "/api/v2/tokens", json={"emails": emails})


class AsyncRoles(AsyncEndpoint):
    """Asynchronous roles endpoint group."""

    async def list(self) -> RoleList:
        data = await self._request("GET", "/api/v2/roles")
        return RoleList.model_validate(data)

    async def update(self, role_id: str, **settings: Any) -> Any:
        return await self._request("PATCH", f"/api/v2/roles/{role_id}", json=settings)

    async def delete(self, role_id: str) -> Any:
        return await self._request("DELETE", f"/api/v2/roles/{role_id}")

    async def invite_coworkers(self, *, emails: list[str]) -> Any:
        return await self._request("POST", "/api/v2/invite/coworkers", json={"emails": emails})

    async def create_coworker(self, *, email: str, first_name: str | None = None, second_name: str | None = None, last_name: str | None = None, phone: str | None = None) -> Any:
        body: dict[str, Any] = {"email": email}
        if first_name:
            body["first_name"] = first_name
        if second_name:
            body["second_name"] = second_name
        if last_name:
            body["last_name"] = last_name
        if phone:
            body["phone"] = phone
        return await self._request("POST", "/api/v2/coworker", json=body)

    async def create_tokens(self, *, emails: list[str], expire_days: str | None = None) -> Any:
        body: dict[str, Any] = {"emails": emails}
        if expire_days:
            body["expire_days"] = expire_days
        return await self._request("POST", "/api/v2/tokens", json=body)

    async def delete_tokens(self, *, emails: list[str]) -> Any:
        return await self._request("DELETE", "/api/v2/tokens", json={"emails": emails})
