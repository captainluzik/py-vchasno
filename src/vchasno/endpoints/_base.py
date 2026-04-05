"""Base classes for sync and async endpoint groups."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vchasno._http import AsyncTransport, SyncTransport


class SyncEndpoint:
    """Base for synchronous endpoint groups."""

    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | list[tuple[str, Any]] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        resp = self._t.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
        )
        if resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return resp.content


class AsyncEndpoint:
    """Base for asynchronous endpoint groups."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | list[tuple[str, Any]] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        resp = await self._t.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
        )
        if resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return resp.content
