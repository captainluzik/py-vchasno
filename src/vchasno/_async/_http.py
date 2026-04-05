"""HTTP transport layer with retry logic for 429 and 5xx responses."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from vchasno.exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    VchasnoAPIError,
)

logger = logging.getLogger("vchasno")

_DEFAULT_TIMEOUT = 30.0
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds
_RETRYABLE_STATUS_CODES = frozenset({429, 502, 503, 504})


def _raise_for_status(response: httpx.Response) -> None:
    """Raise a typed exception based on HTTP status code."""
    if response.is_success:
        return

    status = response.status_code
    body = response.text

    error_classes: dict[int, type[VchasnoAPIError]] = {
        400: BadRequestError,
        401: AuthenticationError,
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


def _retry_delay(response: httpx.Response, attempt: int) -> float:
    """Compute delay: honour ``Retry-After`` header when present, otherwise exponential back-off."""
    retry_after = response.headers.get("retry-after")
    if retry_after is not None:
        try:
            return float(retry_after)
        except (ValueError, TypeError):
            pass
    return _RETRY_BASE_DELAY * (2**attempt)


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
        params: dict[str, Any] | list[tuple[str, Any]] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        attempt = 0
        while True:
            logger.debug("%s %s (attempt %d)", method, path, attempt + 1)
            response = await self._client.request(
                method,
                path,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=headers,
            )
            if response.status_code in _RETRYABLE_STATUS_CODES and attempt < self._max_retries:
                delay = _retry_delay(response, attempt)
                logger.warning(
                    "%s %s returned %d, retrying in %.1fs (attempt %d/%d)",
                    method,
                    path,
                    response.status_code,
                    delay,
                    attempt + 1,
                    self._max_retries,
                )
                await asyncio.sleep(delay)
                attempt += 1
                continue
            _raise_for_status(response)
            return response

    async def close(self) -> None:
        await self._client.aclose()
