"""Vchasno SDK exceptions."""

from __future__ import annotations


class VchasnoError(Exception):
    """Base exception for all Vchasno SDK errors."""


class VchasnoAPIError(VchasnoError):
    """Error returned by the Vchasno API."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response_body: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class AuthenticationError(VchasnoAPIError):
    """401/403 — authentication or authorization failure."""


class RateLimitError(VchasnoAPIError):
    """429 - rate limit exceeded."""


class NotFoundError(VchasnoAPIError):
    """404 - resource not found."""


class BadRequestError(VchasnoAPIError):
    """400 - bad request."""
