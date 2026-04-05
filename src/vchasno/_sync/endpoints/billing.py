"""Billing endpoints."""

from __future__ import annotations

from vchasno._sync.endpoints._base import SyncEndpoint


class SyncBilling(SyncEndpoint):
    """Asynchronous billing endpoint group."""

    def activate_trial(self, *, rate: str = "integration_trial") -> None:
        self._request("POST", "/api/v2/billing/companies/rates/trials", json={"rate": rate})
