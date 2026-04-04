"""Tag models."""

from __future__ import annotations

from pydantic import BaseModel


class Tag(BaseModel):
    """A tag / label."""

    id: str
    name: str
    date_created: str | None = None


class TagList(BaseModel):
    """Response for GET /api/v2/tags."""

    tags: list[Tag]


class TagRole(BaseModel):
    """Role linked to a tag."""

    role_id: str
    tag_id: str
    assigner_id: str | None = None
    date_created: str | None = None


class TagRoleList(BaseModel):
    """Response for GET /api/v2/tags/{tag_id}/roles."""

    roles: list[TagRole]
