"""Document lifecycle state validation."""

from __future__ import annotations

# Status code → set of allowed operation names
_ALLOWED_OPERATIONS: dict[int, frozenset[str]] = {
    7000: frozenset(
        {"update_info", "update_recipient", "set_signers", "set_flow", "delete", "upload_version", "download"}
    ),
    7001: frozenset(
        {
            "sign",
            "send",
            "update_info",
            "update_recipient",
            "set_signers",
            "set_flow",
            "reject",
            "delete",
            "upload_version",
            "download",
        }
    ),
    7002: frozenset({"sign", "reject", "download"}),
    7003: frozenset({"sign", "send", "reject", "download"}),
    7004: frozenset({"sign", "reject", "download"}),
    7006: frozenset({"delete", "archive", "download"}),
    7007: frozenset({"sign", "download"}),
    7008: frozenset({"archive", "download", "delete_request", "unarchive"}),
    7010: frozenset({"sign", "download"}),
    7011: frozenset({"archive", "download", "unarchive"}),
}


def validate_document_state(status: int, operation: str) -> None:
    """Validate that *operation* is allowed for a document with *status*.

    Raises DocumentStateError if the operation is not permitted.
    Unknown statuses (not in the matrix) are allowed — the API may
    introduce new statuses and the SDK should not block them.
    """
    allowed = _ALLOWED_OPERATIONS.get(status)
    if allowed is None:
        return  # unknown status → allow everything
    if operation not in allowed:
        from vchasno.exceptions import DocumentStateError

        raise DocumentStateError(
            f"Operation '{operation}' is not allowed for document in status {status}. "
            f"Allowed operations: {', '.join(sorted(allowed))}",
            current_status=status,
            allowed_statuses=[],
            operation=operation,
        )
