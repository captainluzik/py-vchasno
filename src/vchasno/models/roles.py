"""Role models."""

from __future__ import annotations

from pydantic import BaseModel


class Role(BaseModel):
    """A company role / employee."""

    id: str
    status: str | None = None
    date_created: str | None = None
    email: str | None = None
    position: str | None = None


class RoleList(BaseModel):
    """Response for GET /api/v2/roles."""

    roles: list[Role]
