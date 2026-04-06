"""Tag models."""

from __future__ import annotations

from pydantic import BaseModel


class Tag(BaseModel):
    """A tag / label."""

    model_config = {"extra": "allow"}

    id: str
    name: str
    date_created: str | None = None


class TagList(BaseModel):
    """Response for GET /api/v2/tags."""

    model_config = {"extra": "allow"}

    tags: list[Tag]


class TagRole(BaseModel):
    """Role linked to a tag."""

    model_config = {"extra": "allow"}

    role_id: str
    tag_id: str
    assigner_id: str | None = None
    date_created: str | None = None


class TagRoleList(BaseModel):
    """Response for GET /api/v2/tags/{tag_id}/roles."""

    model_config = {"extra": "allow"}

    roles: list[TagRole]
