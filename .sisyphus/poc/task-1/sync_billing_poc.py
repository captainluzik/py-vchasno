"""Async billing endpoint — PoC for unasyncd transformation validation."""

from __future__ import annotations

from typing import Any


class SyncEndpoint:
    """Base for asynchronous endpoint groups (stub for PoC)."""

    def __init__(self, transport: Any) -> None:
        self._t = transport

    def _request(
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
        resp = self._t.request(
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


class SyncBilling(SyncEndpoint):
    """Asynchronous billing endpoint group."""

    def activate_trial(self, *, rate: str = "integration_trial") -> Any:
        """POST /api/v2/billing/companies/rates/trials."""
        return self._request("POST", "/api/v2/billing/companies/rates/trials", json={"rate": rate})
