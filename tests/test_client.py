"""Tests for vchasno.client (Vchasno / AsyncVchasno)."""

from __future__ import annotations

from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from vchasno.client import AsyncVchasno, Vchasno
from vchasno.endpoints.documents import SyncDocuments, AsyncDocuments
from vchasno.endpoints.signatures import SyncSignatures, AsyncSignatures
from vchasno.endpoints.comments import SyncComments, AsyncComments
from vchasno.endpoints.reviews import SyncReviews, AsyncReviews
from vchasno.endpoints.versions import SyncVersions, AsyncVersions
from vchasno.endpoints.delete_requests import SyncDeleteRequests, AsyncDeleteRequests
from vchasno.endpoints.tags import SyncTags, AsyncTags
from vchasno.endpoints.archive import SyncArchive, AsyncArchive
from vchasno.endpoints.categories import SyncCategories, AsyncCategories
from vchasno.endpoints.fields import SyncFields, AsyncFields
from vchasno.endpoints.children import SyncChildren, AsyncChildren
from vchasno.endpoints.groups import SyncGroups, AsyncGroups
from vchasno.endpoints.roles import SyncRoles, AsyncRoles
from vchasno.endpoints.templates import SyncTemplates, AsyncTemplates
from vchasno.endpoints.reports import SyncReports, AsyncReports
from vchasno.endpoints.cloud_signer import SyncCloudSigner, AsyncCloudSigner
from vchasno.endpoints.billing import SyncBilling, AsyncBilling
from vchasno.endpoints.company import SyncCompany, AsyncCompany


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
