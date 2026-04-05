"""Tags endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.tags import Tag, TagList, TagRoleList


class SyncTags(SyncEndpoint):
    """Asynchronous tags endpoint group."""

    def list(self, *, limit: int | None = None, offset: int | None = None) -> TagList:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        data = self._request("GET", "/api/v2/tags", params=params or None)
        return TagList.model_validate(data)

    def roles(self, tag_id: str) -> TagRoleList:
        data = self._request("GET", f"/api/v2/tags/{tag_id}/roles")
        return TagRoleList.model_validate(data)

    def create_for_documents(self, *, documents_ids: list[str], names: list[str]) -> list[Tag]:
        data = self._request(
            "POST", "/api/v2/tags/documents", json={"documents_ids": documents_ids, "names": names}
        )
        return [Tag.model_validate(t) for t in cast(list[Any], data)]

    def connect_documents(self, *, documents_ids: list[str], tags_ids: list[str]) -> None:
        self._request(
            "POST", "/api/v2/tags/documents/connections", json={"documents_ids": documents_ids, "tags_ids": tags_ids}
        )

    def disconnect_documents(self, *, documents_ids: list[str], tags_ids: list[str]) -> None:
        self._request(
            "DELETE", "/api/v2/tags/documents/connections", json={"documents_ids": documents_ids, "tags_ids": tags_ids}
        )

    def create_for_roles(self, *, roles_ids: list[str], names: list[str]) -> list[Tag]:
        data = self._request("POST", "/api/v2/tags/roles", json={"roles_ids": roles_ids, "names": names})
        return [Tag.model_validate(t) for t in cast(list[Any], data)]

    def connect_roles(self, *, roles_ids: list[str], tags_ids: list[str]) -> None:
        self._request(
            "POST", "/api/v2/tags/roles/connections", json={"roles_ids": roles_ids, "tags_ids": tags_ids}
        )

    def disconnect_roles(self, *, roles_ids: list[str], tags_ids: list[str]) -> None:
        self._request(
            "DELETE", "/api/v2/tags/roles/connections", json={"roles_ids": roles_ids, "tags_ids": tags_ids}
        )
