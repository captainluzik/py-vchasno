"""HTTP transport layer with retry logic for 429 and 5xx responses."""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
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
_MAX_RETRY_DELAY = 60.0  # seconds — cap for Retry-After and exponential backoff
_RETRYABLE_STATUS_CODES = frozenset({429, 502, 503, 504})


def _raise_for_status(response: httpx.Response) -> None:
    """Raise a typed exception based on HTTP status code."""
    if response.is_success:
        return

    status = response.status_code
    body = response.text
    # Truncate message to limit information disclosure in logs/tracebacks.
    # Full body is still available via exception.response_body for programmatic access.
    truncated = body[:500] + "..." if len(body) > 500 else body

    error_classes: dict[int, type[VchasnoAPIError]] = {
        400: BadRequestError,
        401: AuthenticationError,
        403: AuthenticationError,
        404: NotFoundError,
        429: RateLimitError,
    }
    cls = error_classes.get(status, VchasnoAPIError)
    raise cls(
        f"HTTP {status}: {truncated}",
        status_code=status,
        response_body=body,
    )


def _retry_delay(response: httpx.Response, attempt: int) -> float:
    """Compute delay with full jitter: honour Retry-After header, otherwise exponential back-off."""
    retry_after = response.headers.get("retry-after")
    if retry_after is not None:
        try:
            delay = float(retry_after)
            return min(delay, _MAX_RETRY_DELAY)
        except (ValueError, TypeError):
            pass
        # Try HTTP-Date format (RFC 7231)
        try:
            dt = parsedate_to_datetime(retry_after)
            delay = max(0.0, (dt - datetime.now(timezone.utc)).total_seconds())
            return min(delay, _MAX_RETRY_DELAY)
        except Exception:
            pass
    max_delay = _RETRY_BASE_DELAY * (2**attempt)
    return random.uniform(0, min(max_delay, _MAX_RETRY_DELAY))


class SyncTransport:
    """Asynchronous HTTP transport backed by httpx."""

    def __init__(
        self,
        *,
        base_url: str,
        token: str,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _MAX_RETRIES,
        allow_http: bool = False,
    ) -> None:
        if not allow_http and not base_url.startswith("https://"):
            raise ValueError(
                f"base_url must use HTTPS for security. Got: {base_url!r}. "
                "Pass allow_http=True to override (testing only)."
            )
        self._max_retries = max_retries
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": token},
            timeout=timeout,
        )

    def __repr__(self) -> str:
        return f"AsyncTransport(base_url={self._client.base_url!r}, token=***)"

    # -- public ---------------------------------------------------------

    def request(
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
            try:
                response = self._client.request(
                    method,
                    path,
                    params=params,
                    json=json,
                    data=data,
                    files=files,
                    headers=headers,
                )
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                if attempt < self._max_retries:
                    delay = random.uniform(0, min(_RETRY_BASE_DELAY * (2**attempt), _MAX_RETRY_DELAY))
                    logger.warning(
                        "%s %s raised %s, retrying in %.1fs (attempt %d/%d)",
                        method,
                        path,
                        type(exc).__name__,
                        delay,
                        attempt + 1,
                        self._max_retries,
                    )
                    time.sleep(delay)
                    attempt += 1
                    continue
                raise
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
                time.sleep(delay)
                attempt += 1
                continue
            _raise_for_status(response)
            return response

    @contextmanager
    def request_stream(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | list[tuple[str, Any]] | None = None,
        chunk_size: int = 65536,
    ) -> Iterator[Iterator[bytes]]:
        """Stream a response as chunks. Use for large file downloads."""
        with self._client.stream(method, path, params=params) as response:
            _raise_for_status(response)
            yield response.aiter_bytes(chunk_size=chunk_size)

    def close(self) -> None:
        self._client.close()
