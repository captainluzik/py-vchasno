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
    t = SyncTransport(base_url="https://test.example.com", token="test-token")
    t._client = MagicMock(spec=httpx.Client)
    return t


@pytest.fixture()
def async_transport() -> AsyncTransport:
    """An AsyncTransport whose inner client is mocked."""
    t = AsyncTransport(base_url="https://test.example.com", token="test-token")
    t._client = MagicMock(spec=httpx.AsyncClient)
    return t


@pytest.fixture()
def mock_sync_request() -> MagicMock:
    """A mock that can be used as SyncEndpoint._request."""
    return MagicMock()


@pytest.fixture()
def mock_async_request() -> AsyncMock:
    """A mock that can be used as AsyncEndpoint._request."""
    return AsyncMock()
