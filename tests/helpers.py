"""Shared test helpers."""

from __future__ import annotations

import json as _json
from typing import Any

import httpx


def make_response(
    *,
    status_code: int = 200,
    json_data: Any = None,
    content: bytes = b"",
    content_type: str = "application/json",
) -> httpx.Response:
    """Build a fake httpx.Response."""
    headers = {"content-type": content_type}
    if json_data is not None:
        raw = _json.dumps(json_data).encode()
    else:
        raw = content
    return httpx.Response(status_code, headers=headers, content=raw)
