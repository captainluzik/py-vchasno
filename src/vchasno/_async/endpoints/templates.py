"""Templates / scenarios endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno._utils import validate_id
from vchasno.models.common import Template


class AsyncTemplates(AsyncEndpoint):
    """Asynchronous templates endpoint group."""

    async def list(self) -> list[Template]:
        data = await self._request("GET", "/api/v2/templates")
        return [Template.model_validate(t) for t in cast(list[Any], data)]

    async def get(self, template_id: str) -> Template:
        validate_id(template_id, "template_id")
        data = await self._request("GET", f"/api/v2/templates/{template_id}")
        return Template.model_validate(data)
