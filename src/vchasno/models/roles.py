"""Role models."""

from __future__ import annotations

from vchasno.models._base import VchasnoModel


class Role(VchasnoModel):
    """A company role / employee."""

    id: str
    status: str | None = None
    date_created: str | None = None
    email: str | None = None
    position: str | None = None


class RoleList(VchasnoModel):
    """Response for GET /api/v2/roles."""

    roles: list[Role]
