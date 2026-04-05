"""Async billing endpoint — PoC for unasyncd transformation validation."""

from __future__ import annotations

from typing import Any


class AsyncEndpoint:
    """Base for asynchronous endpoint groups (stub for PoC)."""

    def __init__(self, transport: Any) -> None:
        self._t = transport

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | list[tuple[str, Any]] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        resp = await self._t.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
        )
        if resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return resp.content


class AsyncBilling(AsyncEndpoint):
    """Asynchronous billing endpoint group."""

    async def activate_trial(self, *, rate: str = "integration_trial") -> Any:
        """POST /api/v2/billing/companies/rates/trials."""
        return await self._request("POST", "/api/v2/billing/companies/rates/trials", json={"rate": rate})
