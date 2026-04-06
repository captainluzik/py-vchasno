"""Base class for async endpoint groups."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from vchasno._sync._http import SyncTransport

if TYPE_CHECKING:
    pass


class SyncEndpoint:
    """Base for asynchronous endpoint groups."""

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
    ) -> dict[str, Any] | list[Any] | bytes | None:
        resp = self._t.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
        )
        if "json" in (resp.headers.get("content-type") or ""):
            if not resp.content:
                return None
            try:
                return resp.json()
            except ValueError as exc:
                from vchasno.exceptions import VchasnoError

                raise VchasnoError(f"Invalid JSON in API response: {exc}") from exc
        return resp.content

    @contextmanager
    def _request_stream(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | list[tuple[str, Any]] | None = None,
        chunk_size: int = 65536,
    ) -> Iterator[Iterator[bytes]]:
        """Stream response bytes — use for large downloads."""
        with self._t.request_stream(method, path, params=params, chunk_size=chunk_size) as stream:
            yield stream
