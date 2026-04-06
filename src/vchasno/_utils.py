"""Shared utilities: sentinel, param collection, ID validation."""

from __future__ import annotations

import re
from enum import Enum
from typing import Any


class _Unset(Enum):
    """Sentinel type for distinguishing 'not provided' from explicit None."""

    UNSET = "UNSET"

    def __repr__(self) -> str:
        return "UNSET"


#: Sentinel value for optional parameters that were not provided.
#: Distinct from ``None`` — allows PATCH endpoints to explicitly send null.
UNSET: _Unset = _Unset.UNSET

# Keep backward-compatible alias
_UNSET = UNSET

_SAFE_ID_RE = re.compile(r"^[a-zA-Z0-9\-_]+$")


def collect_params(**kwargs: Any) -> dict[str, Any]:
    """Build a query/body dict, dropping UNSET and None values.

    Use for GET params and POST bodies where omitting a key means "no filter".
    """
    return {k: v for k, v in kwargs.items() if v is not UNSET and v is not None}


def collect_update(**kwargs: Any) -> dict[str, Any]:
    """Build a PATCH body dict, dropping only UNSET values (preserves explicit None).

    Use for PATCH endpoints where ``None`` means "clear this field".
    """
    return {k: v for k, v in kwargs.items() if v is not UNSET}


def validate_id(value: str, name: str = "id") -> str:
    """Validate that an ID parameter is safe for URL path interpolation.

    Raises:
        ValueError: If the value contains characters that could cause path traversal.
    """
    if not _SAFE_ID_RE.match(value):
        raise ValueError(
            f"Invalid {name!r}: must contain only alphanumeric characters, hyphens, or underscores. Got: {value!r}"
        )
    return value
