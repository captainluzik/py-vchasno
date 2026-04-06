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


class DocumentStateError(VchasnoError):
    """Raised when an operation is invalid for the current document status."""

    def __init__(
        self,
        message: str,
        *,
        current_status: int,
        allowed_statuses: list[int] | None = None,
        operation: str,
    ) -> None:
        self.current_status = current_status
        self.allowed_statuses = allowed_statuses or []
        self.operation = operation
        super().__init__(message)


class CloudSignerError(VchasnoError):
    """Cloud signer (Vchasno.KEP) specific errors."""

    def __init__(self, message: str, *, session_status: str | None = None) -> None:
        self.session_status = session_status
        super().__init__(message)


class TimeoutError(VchasnoError):  # noqa: A001
    """Polling operation timed out."""

    def __init__(self, message: str, *, elapsed: float, timeout: float) -> None:
        self.elapsed = elapsed
        self.timeout = timeout
        super().__init__(message)


class ValidationError(VchasnoError):
    """SDK-side input validation failure."""

    def __init__(self, message: str, *, field: str | None = None, value: object = None) -> None:
        self.field = field
        self.value = value
        super().__init__(message)
