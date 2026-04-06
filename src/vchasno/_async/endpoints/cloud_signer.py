"""Cloud signer endpoints."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno.exceptions import CloudSignerError, ValidationError
from vchasno.exceptions import TimeoutError as VchasnoTimeoutError
from vchasno.models.cloud_signer import (
    CloudSignerRefresh,
    CloudSignerRefreshCheck,
    CloudSignerSession,
    CloudSignerSessionCheck,
    SignSession,
)
from vchasno.models.enums import SignSessionType

_DURATION_MIN = 60
_DURATION_MAX = 2_592_000  # 30 days


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
    ) -> None:
        """Sign a document using the cloud signer (Vchasno.KEP).

        Warning:
            ``password`` is the private-key password for your cloud signer (KEP).
            Ensure it is never logged or printed.  The SDK does **not** log
            request bodies, but consumer-side logging middleware may capture them.
        """
        body: dict[str, Any] = {"client_id": client_id, "password": password, "document_id": document_id}
        if auth_session_token is not None:
            body["auth_session_token"] = auth_session_token
        if access_token is not None:
            body["access_token"] = access_token
        await self._request("POST", "/api/v2/cloud-signer/sessions/sign-document", json=body)

    async def create_and_wait_session(
        self,
        *,
        duration: int = 3600,
        client_id: str,
        timeout: float = 120.0,
        poll_interval: float = 2.0,
    ) -> str:
        """Create a cloud signer session and poll until the user approves it.

        Returns the session token once the session reaches ``ready`` status.

        Raises:
            ValidationError: If *duration* is outside the 60-2592000 range.
            CloudSignerError: If the session is expired or canceled.
            VchasnoTimeoutError: If the session does not become ready
                within *timeout* seconds.
        """
        if not (_DURATION_MIN <= duration <= _DURATION_MAX):
            raise ValidationError(
                "duration must be between 60 and 2592000 seconds",
                field="duration",
                value=duration,
            )

        session = await self.create_session(duration=duration, client_id=client_id)
        auth_session_id = session.auth_session_id

        start = time.monotonic()
        while time.monotonic() - start < timeout:
            check = await self.check_session(auth_session_id=auth_session_id)
            if check.status == "ready":
                return check.token or ""
            if check.status in ("expired", "canceled"):
                raise CloudSignerError(
                    f"Session {check.status}",
                    session_status=check.status,
                )
            await asyncio.sleep(poll_interval)

        elapsed = time.monotonic() - start
        raise VchasnoTimeoutError(
            f"Session not ready after {elapsed:.1f}s",
            elapsed=elapsed,
            timeout=timeout,
        )

    async def sign_and_wait(
        self,
        *,
        document_id: str,
        client_id: str,
        password: str,
        duration: int = 3600,
        timeout: float = 120.0,
        poll_interval: float = 2.0,
        use_refresh_token: bool = False,
    ) -> None:
        """Sign a document using cloud key with automatic session polling.

        Creates a signing session, waits for user approval in the
        Vchasno.KEP mobile app, then signs the document.

        Warning:
            ``password`` is the private-key password for your cloud signer
            (KEP).  Ensure it is never logged or printed.

        Raises:
            ValidationError: If *duration* is outside the 60-2592000 range.
            CloudSignerError: If the session is expired or canceled.
            VchasnoTimeoutError: If the session does not become ready
                within *timeout* seconds.
        """
        if not (_DURATION_MIN <= duration <= _DURATION_MAX):
            raise ValidationError(
                "duration must be between 60 and 2592000 seconds",
                field="duration",
                value=duration,
            )

        session = await self.create_session(
            duration=duration,
            client_id=client_id,
            use_refresh_token=use_refresh_token,
        )
        auth_session_id = session.auth_session_id

        token: str | None = None
        access_token: str | None = None

        start = time.monotonic()
        while time.monotonic() - start < timeout:
            if use_refresh_token:
                refresh_check = await self.check_refresh_session(
                    auth_session_id=auth_session_id,
                )
                if refresh_check.status == "ready":
                    access_token = refresh_check.access_token
                    break
                status = refresh_check.status
            else:
                check = await self.check_session(
                    auth_session_id=auth_session_id,
                )
                if check.status == "ready":
                    token = check.token
                    break
                status = check.status

            if status in ("expired", "canceled"):
                raise CloudSignerError(
                    f"Session {status}",
                    session_status=status,
                )
            await asyncio.sleep(poll_interval)
        else:
            elapsed = time.monotonic() - start
            raise VchasnoTimeoutError(
                f"Session not ready after {elapsed:.1f}s",
                elapsed=elapsed,
                timeout=timeout,
            )

        if use_refresh_token:
            await self.sign_document(
                client_id=client_id,
                password=password,
                document_id=document_id,
                access_token=access_token,
            )
        else:
            await self.sign_document(
                client_id=client_id,
                password=password,
                document_id=document_id,
                auth_session_token=token,
            )

    async def create_sign_session(
        self,
        *,
        document_id: str,
        edrpou: str,
        email: str,
        session_type: str | SignSessionType,
        on_cancel_url: str | None = None,
        on_finish_url: str | None = None,
    ) -> SignSession:
        body: dict[str, Any] = {
            "document_id": document_id,
            "edrpou": edrpou,
            "email": email,
            "type": session_type,
        }
        if on_cancel_url is not None:
            body["on_cancel_url"] = on_cancel_url
        if on_finish_url is not None:
            body["on_finish_url"] = on_finish_url
        data = await self._request("POST", "/api/v2/sign-sessions", json=body)
        return SignSession.model_validate(data)
