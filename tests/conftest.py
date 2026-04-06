"""Shared fixtures for the test suite."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from vchasno._async._http import AsyncTransport
from vchasno._sync._http import SyncTransport


@pytest.fixture()
def sync_transport() -> SyncTransport:
    """A SyncTransport whose inner client is mocked."""
    t = SyncTransport(base_url="https://test.example.com", token="test-token", allow_http=False)
    original_client = t._client
    t._client = MagicMock(spec=httpx.Client)
    original_client.close()  # Close the real client to avoid resource leak
    return t


@pytest.fixture()
def async_transport() -> AsyncTransport:
    """An AsyncTransport whose inner client is mocked."""
    t = AsyncTransport(base_url="https://test.example.com", token="test-token", allow_http=False)
    original_client = t._client
    t._client = MagicMock(spec=httpx.AsyncClient)
    # Can't await aclose() in sync fixture; mock replacement prevents any real I/O
    del original_client
    return t


@pytest.fixture()
def mock_sync_request() -> MagicMock:
    """A mock that can be used as SyncEndpoint._request."""
    return MagicMock()


@pytest.fixture()
def mock_async_request() -> AsyncMock:
    """A mock that can be used as AsyncEndpoint._request."""
    return AsyncMock()
