"""Enumerations used across the Vchasno API."""

from __future__ import annotations

from enum import IntEnum, StrEnum


class DocumentStatus(IntEnum):
    """Document status codes."""

    UPLOADED = 7000
    READY_TO_SIGN = 7001
    SENT_FOR_FIRST_SIGNATURE = 7002
    PARTIALLY_SIGNED_OWNER = 7003
    AWAITING_RECIPIENT_SIGNATURE = 7004
    REJECTED = 7006
    PARTIALLY_SIGNED_RECIPIENT = 7007
    FULLY_SIGNED = 7008
    SENT_TO_SIGNERS = 7010
    ANNULLED = 7011


class DocumentCategory(IntEnum):
    """Standard document category IDs."""

    NOT_SELECTED = 0
    ACT_OF_SERVICES = 1
    INVOICE = 2
    CONTRACT = 3
    SUPPLEMENTARY_AGREEMENT = 4
    EXPENSE_INVOICE = 5
    TRANSPORT_INVOICE = 6
    EDI_DOCUMENTS = 7
    POWER_OF_ATTORNEY = 8
    SPECIFICATION = 9
    APPLICATION = 10
    ACCEPTANCE_ACT = 11
    RETURN = 12
    ORDER = 13
    APPENDIX = 14
    OTHER = 15
    RECONCILIATION_ACT = 16
    DISCREPANCY_PROTOCOL = 17
    REPORT = 18
    LETTER = 19
    PROTOCOL = 20
    DECREE = 21
    RETURN_ACT = 22
    ADJUSTMENT_CALCULATION = 23
    ADJUSTMENT_ACT = 24
    GUARANTEE_LETTER = 25
    ACCOUNTING_REFERENCE = 26
    WRITE_OFF_ACT = 27
    CORRECTIVE_INVOICE = 28
    ADVANCE_REPORT = 29
    INVENTORY_ACT = 30
    ESTIMATE = 3616
    TECHNICAL_SPECIFICATION = 3617
    FINANCIAL_REFERENCE = 5386
    FINANCIAL_REPORTING = 5387
    OFFER = 6662
    INCOME_INVOICE = 7932
    REFUND_APPLICATION = 8672
    RETURN_EXPENSE_INVOICE = 9765
    COMMISSIONER_REPORT = 9766
    ACT_APPENDIX = 11486
    TRANSPORTATION_REQUEST = 14664
    LICENSE = 17436
    CREDIT_APPLICATION = 18891


class FirstSignBy(StrEnum):
    """Which side signs first."""

    OWNER = "owner"
    RECIPIENT = "recipient"


class ReviewState(StrEnum):
    """Review / approval state."""

    WITHOUT_ANY = "without_any"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class StructuredDataStatus(StrEnum):
    """Structured data recognition status."""

    PENDING = "pending"
    AWAITING_VALIDATION = "awaiting_validation"
    CONFIRMED = "confirmed"
    DOWNLOADED = "downloaded"
    ERROR = "error"


class UserRole(IntEnum):
    """Company role type."""

    REGULAR = 8000
    ADMIN = 8001


class DeleteRequestStatus(StrEnum):
    """Delete request status."""

    NEW = "new"
    REJECTED = "rejected"
    CANCELED = "canceled"
    ACCEPTED = "accepted"


class CloudSignerSessionStatus(StrEnum):
    """Cloud signer session status."""

    INIT = "init"
    READY = "ready"
    PROVIDED = "provided"
    CANCELED = "canceled"
    EXPIRED = "expired"


class SignSessionType(StrEnum):
    """Sign session type."""

    VIEW_SESSION = "view_session"
    SIGN_SESSION = "sign_session"


class AccessSettingsLevel(StrEnum):
    """Document access level."""

    EXTENDED = "extended"
    PRIVATE = "private"


class ViewersStrategy(StrEnum):
    """Viewers editing strategy."""

    ADD = "add"
    REMOVE = "remove"
    REPLACE = "replace"
