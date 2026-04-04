"""Templates / scenarios endpoints."""

from __future__ import annotations

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.common import Template


class SyncTemplates(SyncEndpoint):
    """Synchronous templates endpoint group."""

    def list(self) -> list[Template]:
        """GET /api/v2/templates."""
        data = self._request("GET", "/api/v2/templates")
        return [Template.model_validate(t) for t in data]

    def get(self, template_id: str) -> Template:
        """GET /api/v2/templates/{id}."""
        data = self._request("GET", f"/api/v2/templates/{template_id}")
        return Template.model_validate(data)


class AsyncTemplates(AsyncEndpoint):
    """Asynchronous templates endpoint group."""

    async def list(self) -> list[Template]:
        data = await self._request("GET", "/api/v2/templates")
        return [Template.model_validate(t) for t in data]

    async def get(self, template_id: str) -> Template:
        data = await self._request("GET", f"/api/v2/templates/{template_id}")
        return Template.model_validate(data)
