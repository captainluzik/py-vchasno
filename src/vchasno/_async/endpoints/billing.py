"""Billing endpoints."""

from __future__ import annotations

from vchasno._async.endpoints._base import AsyncEndpoint


class AsyncBilling(AsyncEndpoint):
    """Asynchronous billing endpoint group."""

    async def activate_trial(self, *, rate: str = "integration_trial") -> None:
        await self._request("POST", "/api/v2/billing/companies/rates/trials", json={"rate": rate})
