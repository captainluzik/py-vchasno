"""Templates / scenarios endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.common import Template


class SyncTemplates(SyncEndpoint):
    """Asynchronous templates endpoint group."""

    def list(self) -> list[Template]:
        data = self._request("GET", "/api/v2/templates")
        return [Template.model_validate(t) for t in cast(list[Any], data)]

    def get(self, template_id: str) -> Template:
        data = self._request("GET", f"/api/v2/templates/{template_id}")
        return Template.model_validate(data)
