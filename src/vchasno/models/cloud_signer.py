"""Cloud signer models (camelCase aliases for API compatibility)."""

from __future__ import annotations

from pydantic import Field

from vchasno.models._base import VchasnoModel


class CloudSignerSession(VchasnoModel):
    """Response from creating a cloud signer session."""

    auth_session_id: str = Field(alias="authSessionId")
    is_mobile_logged: bool = Field(alias="isMobileLogged")


class CloudSignerSessionCheck(VchasnoModel):
    """Response from checking a cloud signer session."""

    status: str
    token: str | None = None


class CloudSignerRefreshCheck(VchasnoModel):
    """Response from checking a refresh-token session."""

    status: str
    access_token: str | None = Field(None, alias="accessToken")
    refresh_token: str | None = Field(None, alias="refreshToken")
    expires_in: int | None = Field(None, alias="expiresIn")


class CloudSignerRefresh(VchasnoModel):
    """Response from refreshing an access token."""

    status: str
    access_token: str | None = Field(None, alias="accessToken")
    refresh_token: str | None = Field(None, alias="refreshToken")
    expires_in: int | None = Field(None, alias="expiresIn")


class SignSession(VchasnoModel):
    """Viewing / signing session for personal cabinet integration."""

    id: str
    created_by: str | None = None
    document_id: str | None = None
    document_status: str | None = None
    edrpou: str | None = None
    email: str | None = None
    is_legal: bool | None = None
    on_cancel_url: str | None = None
    on_finish_url: str | None = None
    on_document_comment_hook: str | None = None
    on_document_reject_hook: str | None = None
    on_document_sign_hook: str | None = None
    on_document_view_hook: str | None = None
    role_id: str | None = None
    status: str | None = None
    type: str | None = None
    url: str | None = None
    vendor: str | None = None
