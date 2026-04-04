"""Group / team models."""

from __future__ import annotations

from pydantic import BaseModel


class Group(BaseModel):
    """A user group / team."""

    id: str
    name: str
    created_by: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class GroupMember(BaseModel):
    """A member of a group."""

    id: str
    role_id: str
    group_id: str
    created_by: str | None = None
    date_created: str | None = None
