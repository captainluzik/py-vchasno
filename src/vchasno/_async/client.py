"""Async Vchasno client class."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from vchasno._async._http import AsyncTransport
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

_BASE_URL = "https://edo.vchasno.ua"


class AsyncVchasno:
    """Asynchronous Vchasno.EDO API v2 client.

    Usage::

        async with AsyncVchasno(token="xxx") as client:
            docs = await client.documents.list(status=7008)
    """

    def __init__(
        self,
        *,
        token: str,
        base_url: str = _BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._transport = AsyncTransport(
            base_url=base_url,
            token=token,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.documents = AsyncDocuments(self._transport)
        self.signatures = AsyncSignatures(self._transport)
        self.comments = AsyncComments(self._transport)
        self.reviews = AsyncReviews(self._transport)
        self.versions = AsyncVersions(self._transport)
        self.delete_requests = AsyncDeleteRequests(self._transport)
        self.tags = AsyncTags(self._transport)
        self.archive = AsyncArchive(self._transport)
        self.categories = AsyncCategories(self._transport)
        self.fields = AsyncFields(self._transport)
        self.children = AsyncChildren(self._transport)
        self.groups = AsyncGroups(self._transport)
        self.roles = AsyncRoles(self._transport)
        self.templates = AsyncTemplates(self._transport)
        self.reports = AsyncReports(self._transport)
        self.cloud_signer = AsyncCloudSigner(self._transport)
        self.billing = AsyncBilling(self._transport)
        self.company = AsyncCompany(self._transport)

    async def close(self) -> None:
        await self._transport.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
