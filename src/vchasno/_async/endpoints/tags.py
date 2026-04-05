"""Tags endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno.models.tags import Tag, TagList, TagRoleList


class AsyncTags(AsyncEndpoint):
    """Asynchronous tags endpoint group."""

    async def list(self, *, limit: int | None = None, offset: int | None = None) -> TagList:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        data = await self._request("GET", "/api/v2/tags", params=params or None)
        return TagList.model_validate(data)

    async def roles(self, tag_id: str) -> TagRoleList:
        data = await self._request("GET", f"/api/v2/tags/{tag_id}/roles")
        return TagRoleList.model_validate(data)

    async def create_for_documents(self, *, documents_ids: Sequence[str], names: Sequence[str]) -> list[Tag]:
        data = await self._request(
            "POST", "/api/v2/tags/documents", json={"documents_ids": list(documents_ids), "names": list(names)}
        )
        return [Tag.model_validate(t) for t in cast(list[Any], data)]

    async def connect_documents(self, *, documents_ids: Sequence[str], tags_ids: Sequence[str]) -> None:
        await self._request(
            "POST",
            "/api/v2/tags/documents/connections",
            json={"documents_ids": list(documents_ids), "tags_ids": list(tags_ids)},
        )

    async def disconnect_documents(self, *, documents_ids: Sequence[str], tags_ids: Sequence[str]) -> None:
        await self._request(
            "DELETE",
            "/api/v2/tags/documents/connections",
            json={"documents_ids": list(documents_ids), "tags_ids": list(tags_ids)},
        )

    async def create_for_roles(self, *, roles_ids: Sequence[str], names: Sequence[str]) -> list[Tag]:
        data = await self._request(
            "POST", "/api/v2/tags/roles", json={"roles_ids": list(roles_ids), "names": list(names)}
        )
        return [Tag.model_validate(t) for t in cast(list[Any], data)]

    async def connect_roles(self, *, roles_ids: Sequence[str], tags_ids: Sequence[str]) -> None:
        await self._request(
            "POST", "/api/v2/tags/roles/connections", json={"roles_ids": list(roles_ids), "tags_ids": list(tags_ids)}
        )

    async def disconnect_roles(self, *, roles_ids: Sequence[str], tags_ids: Sequence[str]) -> None:
        await self._request(
            "DELETE", "/api/v2/tags/roles/connections", json={"roles_ids": list(roles_ids), "tags_ids": list(tags_ids)}
        )
