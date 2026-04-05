"""Tests for vchasno._http (transport layer)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from helpers import make_response as _make_response

from vchasno._http import (
    AsyncTransport,
    SyncTransport,
    _raise_for_status,
)
from vchasno.exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    VchasnoAPIError,
)

# ---------------------------------------------------------------------------
# _raise_for_status
# ---------------------------------------------------------------------------


class TestRaiseForStatus:
    def test_success_200(self):
        _raise_for_status(_make_response(status_code=200))

    def test_success_204(self):
        _raise_for_status(_make_response(status_code=204, content_type="text/plain"))

    def test_bad_request_400(self):
        with pytest.raises(BadRequestError) as exc_info:
            _raise_for_status(_make_response(status_code=400, content=b"bad"))
        assert exc_info.value.status_code == 400

    def test_authentication_401(self):
        with pytest.raises(AuthenticationError):
            _raise_for_status(_make_response(status_code=401, content=b"unauthorized"))

    def test_authentication_403(self):
        with pytest.raises(AuthenticationError):
            _raise_for_status(_make_response(status_code=403, content=b"forbidden"))

    def test_not_found_404(self):
        with pytest.raises(NotFoundError):
            _raise_for_status(_make_response(status_code=404, content=b"missing"))

    def test_rate_limit_429(self):
        with pytest.raises(RateLimitError):
            _raise_for_status(_make_response(status_code=429, content=b"slow down"))

    def test_generic_500(self):
        with pytest.raises(VchasnoAPIError) as exc_info:
            _raise_for_status(_make_response(status_code=500, content=b"server err"))
        assert exc_info.value.status_code == 500

    def test_generic_502(self):
        with pytest.raises(VchasnoAPIError):
            _raise_for_status(_make_response(status_code=502, content=b"gateway"))


# ---------------------------------------------------------------------------
# SyncTransport
# ---------------------------------------------------------------------------


class TestSyncTransport:
    def test_init_creates_client(self):
        t = SyncTransport(base_url="https://x.com", token="tok", timeout=10.0, max_retries=2)
        assert t._max_retries == 2
        t.close()

    def test_request_success(self, sync_transport: SyncTransport):
        resp = _make_response(status_code=200, json_data={"ok": True})
        sync_transport._client.request.return_value = resp

        result = sync_transport.request("GET", "/test")
        assert result.status_code == 200
        sync_transport._client.request.assert_called_once_with(
            "GET",
            "/test",
            params=None,
            json=None,
            data=None,
            files=None,
            headers=None,
        )

    def test_request_passes_all_kwargs(self, sync_transport: SyncTransport):
        resp = _make_response(status_code=200)
        sync_transport._client.request.return_value = resp

        sync_transport.request(
            "POST",
            "/path",
            params={"a": "1"},
            json={"b": 2},
            data={"c": "3"},
            files=[("f", ("n", b"data"))],
            headers={"X-Custom": "v"},
        )
        sync_transport._client.request.assert_called_once_with(
            "POST",
            "/path",
            params={"a": "1"},
            json={"b": 2},
            data={"c": "3"},
            files=[("f", ("n", b"data"))],
            headers={"X-Custom": "v"},
        )

    @patch("vchasno._http.time.sleep")
    def test_retry_on_429(self, mock_sleep, sync_transport: SyncTransport):
        r429 = _make_response(status_code=429, content=b"rate limit")
        r200 = _make_response(status_code=200)
        sync_transport._client.request.side_effect = [r429, r200]
        sync_transport._max_retries = 3

        result = sync_transport.request("GET", "/retry")
        assert result.status_code == 200
        mock_sleep.assert_called_once_with(1.0)  # 2^0 * 1

    @patch("vchasno._http.time.sleep")
    def test_retry_exhausted_raises(self, mock_sleep, sync_transport: SyncTransport):
        r429 = _make_response(status_code=429, content=b"rate limit")
        sync_transport._client.request.return_value = r429
        sync_transport._max_retries = 2

        with pytest.raises(RateLimitError):
            sync_transport.request("GET", "/exhaust")
        # 2 retries => sleep called twice (delays 1.0 and 2.0), then final attempt raises
        assert mock_sleep.call_count == 2

    @patch("vchasno._http.time.sleep")
    def test_retry_backoff_delays(self, mock_sleep, sync_transport: SyncTransport):
        r429 = _make_response(status_code=429, content=b"rate limit")
        r200 = _make_response(status_code=200)
        sync_transport._client.request.side_effect = [r429, r429, r200]
        sync_transport._max_retries = 3

        sync_transport.request("GET", "/backoff")
        calls = [c.args[0] for c in mock_sleep.call_args_list]
        assert calls == [1.0, 2.0]

    def test_close(self, sync_transport: SyncTransport):
        sync_transport.close()
        sync_transport._client.close.assert_called_once()

    def test_non_retryable_error(self, sync_transport: SyncTransport):
        resp = _make_response(status_code=400, content=b"bad")
        sync_transport._client.request.return_value = resp
        with pytest.raises(BadRequestError):
            sync_transport.request("GET", "/bad")

    @patch("vchasno._http.time.sleep")
    def test_retry_on_502(self, mock_sleep, sync_transport: SyncTransport):
        r502 = _make_response(status_code=502, content=b"gateway")
        r200 = _make_response(status_code=200)
        sync_transport._client.request.side_effect = [r502, r200]
        sync_transport._max_retries = 3

        result = sync_transport.request("GET", "/retry-502")
        assert result.status_code == 200
        mock_sleep.assert_called_once()

    @patch("vchasno._http.time.sleep")
    def test_retry_on_503(self, mock_sleep, sync_transport: SyncTransport):
        r503 = _make_response(status_code=503, content=b"unavailable")
        r200 = _make_response(status_code=200)
        sync_transport._client.request.side_effect = [r503, r200]
        sync_transport._max_retries = 3

        result = sync_transport.request("GET", "/retry-503")
        assert result.status_code == 200

    @patch("vchasno._http.time.sleep")
    def test_retry_on_504(self, mock_sleep, sync_transport: SyncTransport):
        r504 = _make_response(status_code=504, content=b"timeout")
        r200 = _make_response(status_code=200)
        sync_transport._client.request.side_effect = [r504, r200]
        sync_transport._max_retries = 3

        result = sync_transport.request("GET", "/retry-504")
        assert result.status_code == 200

    @patch("vchasno._http.time.sleep")
    def test_retry_after_header(self, mock_sleep, sync_transport: SyncTransport):
        """Retry-After header should override exponential backoff."""
        r429 = httpx.Response(429, headers={"content-type": "text/plain", "retry-after": "5"}, content=b"limit")
        r200 = _make_response(status_code=200)
        sync_transport._client.request.side_effect = [r429, r200]
        sync_transport._max_retries = 3

        sync_transport.request("GET", "/retry-after")
        mock_sleep.assert_called_once_with(5.0)


# ---------------------------------------------------------------------------
# AsyncTransport
# ---------------------------------------------------------------------------


class TestAsyncTransport:
    def test_init_creates_client(self):
        t = AsyncTransport(base_url="https://x.com", token="tok", timeout=10.0, max_retries=2)
        assert t._max_retries == 2

    @pytest.mark.asyncio
    async def test_request_success(self, async_transport: AsyncTransport):
        resp = _make_response(status_code=200, json_data={"ok": True})
        async_transport._client.request = AsyncMock(return_value=resp)

        result = await async_transport.request("GET", "/test")
        assert result.status_code == 200

    @pytest.mark.asyncio
    @patch("vchasno._http.asyncio.sleep", new_callable=AsyncMock)
    async def test_retry_on_429(self, mock_sleep, async_transport: AsyncTransport):
        r429 = _make_response(status_code=429, content=b"rate limit")
        r200 = _make_response(status_code=200)
        async_transport._client.request = AsyncMock(side_effect=[r429, r200])
        async_transport._max_retries = 3

        result = await async_transport.request("GET", "/retry")
        assert result.status_code == 200
        mock_sleep.assert_called_once_with(1.0)

    @pytest.mark.asyncio
    @patch("vchasno._http.asyncio.sleep", new_callable=AsyncMock)
    async def test_retry_exhausted_raises(self, mock_sleep, async_transport: AsyncTransport):
        r429 = _make_response(status_code=429, content=b"rate limit")
        async_transport._client.request = AsyncMock(return_value=r429)
        async_transport._max_retries = 2

        with pytest.raises(RateLimitError):
            await async_transport.request("GET", "/exhaust")
        assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    @patch("vchasno._http.asyncio.sleep", new_callable=AsyncMock)
    async def test_retry_backoff_delays(self, mock_sleep, async_transport: AsyncTransport):
        r429 = _make_response(status_code=429, content=b"rate limit")
        r200 = _make_response(status_code=200)
        async_transport._client.request = AsyncMock(side_effect=[r429, r429, r200])
        async_transport._max_retries = 3

        await async_transport.request("GET", "/backoff")
        calls = [c.args[0] for c in mock_sleep.call_args_list]
        assert calls == [1.0, 2.0]

    @pytest.mark.asyncio
    async def test_close(self, async_transport: AsyncTransport):
        async_transport._client.aclose = AsyncMock()
        await async_transport.close()
        async_transport._client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_passes_all_kwargs(self, async_transport: AsyncTransport):
        resp = _make_response(status_code=200)
        async_transport._client.request = AsyncMock(return_value=resp)

        await async_transport.request(
            "POST",
            "/path",
            params={"a": "1"},
            json={"b": 2},
            data={"c": "3"},
            files=[("f", ("n", b"data"))],
            headers={"X-Custom": "v"},
        )
        async_transport._client.request.assert_called_once_with(
            "POST",
            "/path",
            params={"a": "1"},
            json={"b": 2},
            data={"c": "3"},
            files=[("f", ("n", b"data"))],
            headers={"X-Custom": "v"},
        )
