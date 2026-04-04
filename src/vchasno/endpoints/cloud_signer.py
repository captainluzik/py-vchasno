"""Cloud signer endpoints."""

from __future__ import annotations

from typing import Any

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.cloud_signer import (
    CloudSignerRefresh,
    CloudSignerRefreshCheck,
    CloudSignerSession,
    CloudSignerSessionCheck,
    SignSession,
)


class SyncCloudSigner(SyncEndpoint):
    """Synchronous cloud signer endpoint group."""

    def create_session(self, *, duration: int, client_id: str, use_refresh_token: bool = False) -> CloudSignerSession:
        """POST /api/v2/cloud-signer/sessions/create."""
        data = self._request(
            "POST",
            "/api/v2/cloud-signer/sessions/create",
            json={
                "duration": duration,
                "client_id": client_id,
                "use_refresh_token": use_refresh_token,
            },
        )
        return CloudSignerSession.model_validate(data)

    def check_session(self, *, auth_session_id: str) -> CloudSignerSessionCheck:
        """POST /api/v2/cloud-signer/sessions/check."""
        data = self._request("POST", "/api/v2/cloud-signer/sessions/check", json={"auth_session_id": auth_session_id})
        return CloudSignerSessionCheck.model_validate(data)

    def check_refresh_session(self, *, auth_session_id: str) -> CloudSignerRefreshCheck:
        """POST /api/v2/cloud-signer/sessions/refresh/check."""
        data = self._request(
            "POST", "/api/v2/cloud-signer/sessions/refresh/check", json={"auth_session_id": auth_session_id}
        )
        return CloudSignerRefreshCheck.model_validate(data)

    def refresh_token(self, *, auth_session_id: str, refresh_token: str) -> CloudSignerRefresh:
        """POST /api/v2/cloud-signer/sessions/refresh."""
        data = self._request(
            "POST",
            "/api/v2/cloud-signer/sessions/refresh",
            json={
                "auth_session_id": auth_session_id,
                "refresh_token": refresh_token,
            },
        )
        return CloudSignerRefresh.model_validate(data)

    def sign_document(
        self,
        *,
        client_id: str,
        password: str,
        document_id: str,
        auth_session_token: str | None = None,
        access_token: str | None = None,
    ) -> Any:
        """POST /api/v2/cloud-signer/sessions/sign-document."""
        body: dict[str, Any] = {"client_id": client_id, "password": password, "document_id": document_id}
        if auth_session_token is not None:
            body["auth_session_token"] = auth_session_token
        if access_token is not None:
            body["access_token"] = access_token
        return self._request("POST", "/api/v2/cloud-signer/sessions/sign-document", json=body)

    def create_sign_session(
        self,
        *,
        document_id: str,
        edrpou: str,
        email: str,
        type: str,
        on_cancel_url: str | None = None,
        on_finish_url: str | None = None,
    ) -> SignSession:
        """POST /api/v2/sign-sessions."""
        body: dict[str, Any] = {"document_id": document_id, "edrpou": edrpou, "email": email, "type": type}
        if on_cancel_url is not None:
            body["on_cancel_url"] = on_cancel_url
        if on_finish_url is not None:
            body["on_finish_url"] = on_finish_url
        data = self._request("POST", "/api/v2/sign-sessions", json=body)
        return SignSession.model_validate(data)


class AsyncCloudSigner(AsyncEndpoint):
    """Asynchronous cloud signer endpoint group."""

    async def create_session(
        self, *, duration: int, client_id: str, use_refresh_token: bool = False
    ) -> CloudSignerSession:
        data = await self._request(
            "POST",
            "/api/v2/cloud-signer/sessions/create",
            json={
                "duration": duration,
                "client_id": client_id,
                "use_refresh_token": use_refresh_token,
            },
        )
        return CloudSignerSession.model_validate(data)

    async def check_session(self, *, auth_session_id: str) -> CloudSignerSessionCheck:
        data = await self._request(
            "POST", "/api/v2/cloud-signer/sessions/check", json={"auth_session_id": auth_session_id}
        )
        return CloudSignerSessionCheck.model_validate(data)

    async def check_refresh_session(self, *, auth_session_id: str) -> CloudSignerRefreshCheck:
        data = await self._request(
            "POST", "/api/v2/cloud-signer/sessions/refresh/check", json={"auth_session_id": auth_session_id}
        )
        return CloudSignerRefreshCheck.model_validate(data)

    async def refresh_token(self, *, auth_session_id: str, refresh_token: str) -> CloudSignerRefresh:
        data = await self._request(
            "POST",
            "/api/v2/cloud-signer/sessions/refresh",
            json={
                "auth_session_id": auth_session_id,
                "refresh_token": refresh_token,
            },
        )
        return CloudSignerRefresh.model_validate(data)

    async def sign_document(
        self,
        *,
        client_id: str,
        password: str,
        document_id: str,
        auth_session_token: str | None = None,
        access_token: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {"client_id": client_id, "password": password, "document_id": document_id}
        if auth_session_token is not None:
            body["auth_session_token"] = auth_session_token
        if access_token is not None:
            body["access_token"] = access_token
        return await self._request("POST", "/api/v2/cloud-signer/sessions/sign-document", json=body)

    async def create_sign_session(
        self,
        *,
        document_id: str,
        edrpou: str,
        email: str,
        type: str,
        on_cancel_url: str | None = None,
        on_finish_url: str | None = None,
    ) -> SignSession:
        body: dict[str, Any] = {"document_id": document_id, "edrpou": edrpou, "email": email, "type": type}
        if on_cancel_url is not None:
            body["on_cancel_url"] = on_cancel_url
        if on_finish_url is not None:
            body["on_finish_url"] = on_finish_url
        data = await self._request("POST", "/api/v2/sign-sessions", json=body)
        return SignSession.model_validate(data)
