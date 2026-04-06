"""Tests for vchasno.client (Vchasno / AsyncVchasno)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from vchasno._async.client import AsyncVchasno
from vchasno._async.endpoints.archive import AsyncArchive
from vchasno._async.endpoints.billing import AsyncBilling
from vchasno._async.endpoints.categories import AsyncCategories
from vchasno._async.endpoints.children import AsyncChildren
from vchasno._async.endpoints.cloud_signer import AsyncCloudSigner
from vchasno._async.endpoints.comments import AsyncComments
from vchasno._async.endpoints.company import AsyncCompany
from vchasno._async.endpoints.delete_requests import AsyncDeleteRequests
from vchasno._async.endpoints.documents import AsyncDocuments
from vchasno._async.endpoints.fields import AsyncFields
from vchasno._async.endpoints.groups import AsyncGroups
from vchasno._async.endpoints.reports import AsyncReports
from vchasno._async.endpoints.reviews import AsyncReviews
from vchasno._async.endpoints.roles import AsyncRoles
from vchasno._async.endpoints.signatures import AsyncSignatures
from vchasno._async.endpoints.tags import AsyncTags
from vchasno._async.endpoints.templates import AsyncTemplates
from vchasno._async.endpoints.versions import AsyncVersions
from vchasno._sync.client import Vchasno
from vchasno._sync.endpoints.archive import SyncArchive
from vchasno._sync.endpoints.billing import SyncBilling
from vchasno._sync.endpoints.categories import SyncCategories
from vchasno._sync.endpoints.children import SyncChildren
from vchasno._sync.endpoints.cloud_signer import SyncCloudSigner
from vchasno._sync.endpoints.comments import SyncComments
from vchasno._sync.endpoints.company import SyncCompany
from vchasno._sync.endpoints.delete_requests import SyncDeleteRequests
from vchasno._sync.endpoints.documents import SyncDocuments
from vchasno._sync.endpoints.fields import SyncFields
from vchasno._sync.endpoints.groups import SyncGroups
from vchasno._sync.endpoints.reports import SyncReports
from vchasno._sync.endpoints.reviews import SyncReviews
from vchasno._sync.endpoints.roles import SyncRoles
from vchasno._sync.endpoints.signatures import SyncSignatures
from vchasno._sync.endpoints.tags import SyncTags
from vchasno._sync.endpoints.templates import SyncTemplates
from vchasno._sync.endpoints.versions import SyncVersions


class TestVchasno:
    def test_init_creates_all_endpoints(self):
        client = Vchasno(token="tok")
        assert isinstance(client.documents, SyncDocuments)
        assert isinstance(client.signatures, SyncSignatures)
        assert isinstance(client.comments, SyncComments)
        assert isinstance(client.reviews, SyncReviews)
        assert isinstance(client.versions, SyncVersions)
        assert isinstance(client.delete_requests, SyncDeleteRequests)
        assert isinstance(client.tags, SyncTags)
        assert isinstance(client.archive, SyncArchive)
        assert isinstance(client.categories, SyncCategories)
        assert isinstance(client.fields, SyncFields)
        assert isinstance(client.children, SyncChildren)
        assert isinstance(client.groups, SyncGroups)
        assert isinstance(client.roles, SyncRoles)
        assert isinstance(client.templates, SyncTemplates)
        assert isinstance(client.reports, SyncReports)
        assert isinstance(client.cloud_signer, SyncCloudSigner)
        assert isinstance(client.billing, SyncBilling)
        assert isinstance(client.company, SyncCompany)
        client.close()

    def test_context_manager(self):
        with Vchasno(token="tok") as client:
            assert isinstance(client, Vchasno)

    def test_close_calls_transport_close(self):
        client = Vchasno(token="tok")
        client._transport = MagicMock()
        client.close()
        client._transport.close.assert_called_once()

    def test_custom_params(self):
        client = Vchasno(token="tok", base_url="https://custom.url", timeout=10.0, max_retries=5)
        assert client._transport._max_retries == 5
        client.close()


class TestAsyncVchasno:
    def test_init_creates_all_endpoints(self):
        client = AsyncVchasno(token="tok")
        assert isinstance(client.documents, AsyncDocuments)
        assert isinstance(client.signatures, AsyncSignatures)
        assert isinstance(client.comments, AsyncComments)
        assert isinstance(client.reviews, AsyncReviews)
        assert isinstance(client.versions, AsyncVersions)
        assert isinstance(client.delete_requests, AsyncDeleteRequests)
        assert isinstance(client.tags, AsyncTags)
        assert isinstance(client.archive, AsyncArchive)
        assert isinstance(client.categories, AsyncCategories)
        assert isinstance(client.fields, AsyncFields)
        assert isinstance(client.children, AsyncChildren)
        assert isinstance(client.groups, AsyncGroups)
        assert isinstance(client.roles, AsyncRoles)
        assert isinstance(client.templates, AsyncTemplates)
        assert isinstance(client.reports, AsyncReports)
        assert isinstance(client.cloud_signer, AsyncCloudSigner)
        assert isinstance(client.billing, AsyncBilling)
        assert isinstance(client.company, AsyncCompany)

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        client = AsyncVchasno(token="tok")
        client._transport = MagicMock()
        client._transport.close = AsyncMock()
        async with client as c:
            assert isinstance(c, AsyncVchasno)
        client._transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_calls_transport_close(self):
        client = AsyncVchasno(token="tok")
        client._transport = MagicMock()
        client._transport.close = AsyncMock()
        await client.close()
        client._transport.close.assert_called_once()
