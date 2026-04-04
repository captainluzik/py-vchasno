"""Billing endpoints."""

from __future__ import annotations

from typing import Any

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint


class SyncBilling(SyncEndpoint):
    """Synchronous billing endpoint group."""

    def activate_trial(self, *, rate: str = "integration_trial") -> Any:
        """POST /api/v2/billing/companies/rates/trials."""
        return self._request("POST", "/api/v2/billing/companies/rates/trials", json={"rate": rate})


class AsyncBilling(AsyncEndpoint):
    """Asynchronous billing endpoint group."""

    async def activate_trial(self, *, rate: str = "integration_trial") -> Any:
        return await self._request("POST", "/api/v2/billing/companies/rates/trials", json={"rate": rate})
