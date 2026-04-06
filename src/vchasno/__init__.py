"""Vchasno.EDO API v2 Python SDK."""

from __future__ import annotations

from vchasno._async._pagination import AsyncCursorPage
from vchasno._async.client import AsyncVchasno
from vchasno._sync._pagination import SyncCursorPage
from vchasno._sync.client import Vchasno
from vchasno.exceptions import (
    AuthenticationError,
    BadRequestError,
    CloudSignerError,
    DocumentStateError,
    NotFoundError,
    RateLimitError,
    TimeoutError,  # noqa: A004
    ValidationError,
    VchasnoAPIError,
    VchasnoError,
)
from vchasno.models._base import VchasnoModel

__version__ = "1.0.0"

from typing import Any

CursorPage = AsyncCursorPage[Any] | SyncCursorPage[Any]

__all__ = [
    "AsyncVchasno",
    "AsyncCursorPage",
    "AuthenticationError",
    "BadRequestError",
    "CloudSignerError",
    "CursorPage",
    "DocumentStateError",
    "NotFoundError",
    "RateLimitError",
    "SyncCursorPage",
    "TimeoutError",
    "ValidationError",
    "Vchasno",
    "VchasnoAPIError",
    "VchasnoError",
    "VchasnoModel",
]
