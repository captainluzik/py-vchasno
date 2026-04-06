"""Async Vchasno client class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from vchasno._sync._http import SyncTransport
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

if TYPE_CHECKING:
    from typing import Self


_BASE_URL = "https://edo.vchasno.ua"


class Vchasno:
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
        allow_http: bool = False,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._transport = SyncTransport(
            base_url=base_url,
            token=token,
            timeout=timeout,
            max_retries=max_retries,
            allow_http=allow_http,
            http_client=http_client,
        )
        self.documents = SyncDocuments(self._transport)
        self.signatures = SyncSignatures(self._transport)
        self.comments = SyncComments(self._transport)
        self.reviews = SyncReviews(self._transport)
        self.versions = SyncVersions(self._transport)
        self.delete_requests = SyncDeleteRequests(self._transport)
        self.tags = SyncTags(self._transport)
        self.archive = SyncArchive(self._transport)
        self.categories = SyncCategories(self._transport)
        self.fields = SyncFields(self._transport)
        self.children = SyncChildren(self._transport)
        self.groups = SyncGroups(self._transport)
        self.roles = SyncRoles(self._transport)
        self.templates = SyncTemplates(self._transport)
        self.reports = SyncReports(self._transport)
        self.cloud_signer = SyncCloudSigner(self._transport)
        self.billing = SyncBilling(self._transport)
        self.company = SyncCompany(self._transport)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
