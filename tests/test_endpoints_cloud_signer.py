"""Tests for vchasno.endpoints.cloud_signer."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from vchasno._async.endpoints.cloud_signer import AsyncCloudSigner
from vchasno._sync.endpoints.cloud_signer import SyncCloudSigner
from vchasno.models.cloud_signer import (
    CloudSignerRefresh,
    CloudSignerRefreshCheck,
    CloudSignerSession,
    CloudSignerSessionCheck,
    SignSession,
)


class TestSyncCloudSigner:
    def _make(self):
        ep = SyncCloudSigner(MagicMock())
        ep._request = MagicMock()
        return ep, ep._request

    def test_create_session(self):
        ep, req = self._make()
        req.return_value = {"authSessionId": "s1", "isMobileLogged": False}
        result = ep.create_session(duration=300, client_id="c1")
        assert isinstance(result, CloudSignerSession)
        assert result.auth_session_id == "s1"

    def test_create_session_with_refresh(self):
        ep, req = self._make()
        req.return_value = {"authSessionId": "s1", "isMobileLogged": False}
        ep.create_session(duration=300, client_id="c1", use_refresh_token=True)
        call_json = req.call_args.kwargs["json"]
        assert call_json["use_refresh_token"] is True

    def test_check_session(self):
        ep, req = self._make()
        req.return_value = {"status": "ready", "token": "tok"}
        result = ep.check_session(auth_session_id="s1")
        assert isinstance(result, CloudSignerSessionCheck)

    def test_check_refresh_session(self):
        ep, req = self._make()
        req.return_value = {"status": "ready", "accessToken": "at", "refreshToken": "rt", "expiresIn": 3600}
        result = ep.check_refresh_session(auth_session_id="s1")
        assert isinstance(result, CloudSignerRefreshCheck)
        assert result.access_token == "at"

    def test_refresh_token(self):
        ep, req = self._make()
        req.return_value = {"status": "ok", "accessToken": "at", "refreshToken": "rt", "expiresIn": 100}
        result = ep.refresh_token(auth_session_id="s1", refresh_token="rt")
        assert isinstance(result, CloudSignerRefresh)

    def test_sign_document_minimal(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.sign_document(client_id="c1", password="p", document_id="d1")
        call_json = req.call_args.kwargs["json"]
        assert "auth_session_token" not in call_json
        assert "access_token" not in call_json

    def test_sign_document_with_tokens(self):
        ep, req = self._make()
        req.return_value = {"ok": True}
        ep.sign_document(client_id="c1", password="p", document_id="d1", auth_session_token="ast", access_token="at")
        call_json = req.call_args.kwargs["json"]
        assert call_json["auth_session_token"] == "ast"
        assert call_json["access_token"] == "at"

    def test_create_sign_session_minimal(self):
        ep, req = self._make()
        req.return_value = {"id": "ss1"}
        result = ep.create_sign_session(document_id="d1", edrpou="e", email="e@m.com", session_type="sign_session")
        assert isinstance(result, SignSession)
        call_json = req.call_args.kwargs["json"]
        assert "on_cancel_url" not in call_json

    def test_create_sign_session_with_urls(self):
        ep, req = self._make()
        req.return_value = {"id": "ss1"}
        ep.create_sign_session(
            document_id="d1",
            edrpou="e",
            email="e@m.com",
            session_type="sign_session",
            on_cancel_url="cu",
            on_finish_url="fu",
        )
        call_json = req.call_args.kwargs["json"]
        assert call_json["on_cancel_url"] == "cu"
        assert call_json["on_finish_url"] == "fu"


class TestAsyncCloudSigner:
    def _make(self):
        ep = AsyncCloudSigner(MagicMock())
        ep._request = AsyncMock()
        return ep, ep._request

    @pytest.mark.asyncio
    async def test_create_session(self):
        ep, req = self._make()
        req.return_value = {"authSessionId": "s1", "isMobileLogged": False}
        result = await ep.create_session(duration=300, client_id="c1")
        assert isinstance(result, CloudSignerSession)

    @pytest.mark.asyncio
    async def test_check_session(self):
        ep, req = self._make()
        req.return_value = {"status": "ready"}
        result = await ep.check_session(auth_session_id="s1")
        assert isinstance(result, CloudSignerSessionCheck)

    @pytest.mark.asyncio
    async def test_check_refresh_session(self):
        ep, req = self._make()
        req.return_value = {"status": "ready"}
        result = await ep.check_refresh_session(auth_session_id="s1")
        assert isinstance(result, CloudSignerRefreshCheck)

    @pytest.mark.asyncio
    async def test_refresh_token(self):
        ep, req = self._make()
        req.return_value = {"status": "ok"}
        result = await ep.refresh_token(auth_session_id="s1", refresh_token="rt")
        assert isinstance(result, CloudSignerRefresh)

    @pytest.mark.asyncio
    async def test_sign_document_minimal(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.sign_document(client_id="c1", password="p", document_id="d1")
        call_json = req.call_args.kwargs["json"]
        assert "auth_session_token" not in call_json

    @pytest.mark.asyncio
    async def test_sign_document_with_tokens(self):
        ep, req = self._make()
        req.return_value = {}
        await ep.sign_document(
            client_id="c1", password="p", document_id="d1", auth_session_token="ast", access_token="at"
        )
        call_json = req.call_args.kwargs["json"]
        assert call_json["access_token"] == "at"

    @pytest.mark.asyncio
    async def test_create_sign_session_minimal(self):
        ep, req = self._make()
        req.return_value = {"id": "ss1"}
        result = await ep.create_sign_session(document_id="d1", edrpou="e", email="e@m.com", session_type="sign")
        assert isinstance(result, SignSession)

    @pytest.mark.asyncio
    async def test_create_sign_session_with_urls(self):
        ep, req = self._make()
        req.return_value = {"id": "ss1"}
        await ep.create_sign_session(
            document_id="d1", edrpou="e", email="e@m.com", session_type="sign", on_cancel_url="cu", on_finish_url="fu"
        )
        call_json = req.call_args.kwargs["json"]
        assert call_json["on_cancel_url"] == "cu"
