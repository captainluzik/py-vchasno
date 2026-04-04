"""HTTP transport layer with retry logic for 429 responses."""

from __future__ import annotations

import time
import asyncio
from typing import Any

import httpx

from vchasno.exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    VchasnoAPIError,
)

_DEFAULT_TIMEOUT = 30.0
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds


def _raise_for_status(response: httpx.Response) -> None:
    """Raise a typed exception based on HTTP status code."""
    if response.is_success:
        return

    status = response.status_code
    body = response.text

    error_classes: dict[int, type[VchasnoAPIError]] = {
        400: BadRequestError,
        403: AuthenticationError,
        404: NotFoundError,
        429: RateLimitError,
    }
    cls = error_classes.get(status, VchasnoAPIError)
    raise cls(
        f"HTTP {status}: {body}",
        status_code=status,
        response_body=body,
    )


class SyncTransport:
    """Synchronous HTTP transport backed by httpx."""

    def __init__(
        self,
        *,
        base_url: str,
        token: str,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self._max_retries = max_retries
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": token},
            timeout=timeout,
        )

    # -- public ---------------------------------------------------------

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        attempt = 0
        while True:
            response = self._client.request(
                method,
                path,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=headers,
            )
            if response.status_code == 429 and attempt < self._max_retries:
                delay = _RETRY_BASE_DELAY * (2**attempt)
                time.sleep(delay)
                attempt += 1
                continue
            _raise_for_status(response)
            return response

    def close(self) -> None:
        self._client.close()


class AsyncTransport:
    """Asynchronous HTTP transport backed by httpx."""

    def __init__(
        self,
        *,
        base_url: str,
        token: str,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": token},
            timeout=timeout,
        )

    # -- public ---------------------------------------------------------

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        attempt = 0
        while True:
            response = await self._client.request(
                method,
                path,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=headers,
            )
            if response.status_code == 429 and attempt < self._max_retries:
                delay = _RETRY_BASE_DELAY * (2**attempt)
                await asyncio.sleep(delay)
                attempt += 1
                continue
            _raise_for_status(response)
            return response

    async def close(self) -> None:
        await self._client.aclose()
