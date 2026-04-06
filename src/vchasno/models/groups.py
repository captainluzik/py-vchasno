"""Group / team models."""

from __future__ import annotations

from vchasno.models._base import VchasnoModel


class Group(VchasnoModel):
    """A user group / team."""

    id: str
    name: str
    created_by: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class GroupMember(VchasnoModel):
    """A member of a group."""

    id: str
    role_id: str
    group_id: str
    created_by: str | None = None
    date_created: str | None = None
