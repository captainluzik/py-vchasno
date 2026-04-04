"""Tests for vchasno.endpoints._base."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint

from helpers import make_response as _make_response


class TestSyncEndpoint:
    def test_request_json_response(self):
        transport = MagicMock()
        resp = _make_response(status_code=200, json_data={"key": "val"})
        transport.request.return_value = resp

        ep = SyncEndpoint(transport)
        result = ep._request("GET", "/path")
        assert result == {"key": "val"}

    def test_request_binary_response(self):
        transport = MagicMock()
        resp = _make_response(status_code=200, content=b"raw bytes", content_type="application/octet-stream")
        transport.request.return_value = resp

        ep = SyncEndpoint(transport)
        result = ep._request("GET", "/dl")
        assert result == b"raw bytes"

    def test_request_passes_params(self):
        transport = MagicMock()
        resp = _make_response(status_code=200, json_data={})
        transport.request.return_value = resp

        ep = SyncEndpoint(transport)
        ep._request("POST", "/p", params={"a": 1}, json={"b": 2}, data={"c": 3}, files=[("f", ("n", b"d"))], headers={"H": "V"})
        transport.request.assert_called_once_with(
            "POST", "/p", params={"a": 1}, json={"b": 2}, data={"c": 3}, files=[("f", ("n", b"d"))], headers={"H": "V"},
        )

    def test_request_empty_content_type(self):
        transport = MagicMock()
        resp = httpx.Response(200, headers={}, content=b"stuff")
        transport.request.return_value = resp

        ep = SyncEndpoint(transport)
        result = ep._request("GET", "/no-ct")
        assert result == b"stuff"


class TestAsyncEndpoint:
    @pytest.mark.asyncio
    async def test_request_json_response(self):
        transport = MagicMock()
        resp = _make_response(status_code=200, json_data={"key": "val"})
        transport.request = AsyncMock(return_value=resp)

        ep = AsyncEndpoint(transport)
        result = await ep._request("GET", "/path")
        assert result == {"key": "val"}

    @pytest.mark.asyncio
    async def test_request_binary_response(self):
        transport = MagicMock()
        resp = _make_response(status_code=200, content=b"raw bytes", content_type="application/octet-stream")
        transport.request = AsyncMock(return_value=resp)

        ep = AsyncEndpoint(transport)
        result = await ep._request("GET", "/dl")
        assert result == b"raw bytes"

    @pytest.mark.asyncio
    async def test_request_passes_params(self):
        transport = MagicMock()
        resp = _make_response(status_code=200, json_data={})
        transport.request = AsyncMock(return_value=resp)

        ep = AsyncEndpoint(transport)
        await ep._request("POST", "/p", params={"a": 1}, json={"b": 2}, data={"c": 3}, files=[("f", ("n", b"d"))], headers={"H": "V"})
        transport.request.assert_called_once_with(
            "POST", "/p", params={"a": 1}, json={"b": 2}, data={"c": 3}, files=[("f", ("n", b"d"))], headers={"H": "V"},
        )
