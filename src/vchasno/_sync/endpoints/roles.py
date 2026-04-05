"""Roles / employees endpoints."""

from __future__ import annotations

from typing import Any

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.roles import RoleList


class SyncRoles(SyncEndpoint):
    """Asynchronous roles endpoint group."""

    def list(self) -> RoleList:
        data = self._request("GET", "/api/v2/roles")
        return RoleList.model_validate(data)

    def update(self, role_id: str, **settings: Any) -> Any:
        return self._request("PATCH", f"/api/v2/roles/{role_id}", json=settings)

    def delete(self, role_id: str) -> Any:
        return self._request("DELETE", f"/api/v2/roles/{role_id}")

    def invite_coworkers(self, *, emails: list[str]) -> Any:
        return self._request("POST", "/api/v2/invite/coworkers", json={"emails": emails})

    def create_coworker(
        self,
        *,
        email: str,
        first_name: str | None = None,
        second_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {"email": email}
        if first_name is not None:
            body["first_name"] = first_name
        if second_name is not None:
            body["second_name"] = second_name
        if last_name is not None:
            body["last_name"] = last_name
        if phone is not None:
            body["phone"] = phone
        return self._request("POST", "/api/v2/coworker", json=body)

    def create_tokens(self, *, emails: list[str], expire_days: str | None = None) -> Any:
        body: dict[str, Any] = {"emails": emails}
        if expire_days is not None:
            body["expire_days"] = expire_days
        return self._request("POST", "/api/v2/tokens", json=body)

    def delete_tokens(self, *, emails: list[str]) -> Any:
        return self._request("DELETE", "/api/v2/tokens", json={"emails": emails})
