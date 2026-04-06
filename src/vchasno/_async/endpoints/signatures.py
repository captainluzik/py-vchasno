"""Signatures endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno._utils import validate_id
from vchasno.models.documents import FlowEntry, SignatureDetail


class AsyncSignatures(AsyncEndpoint):
    """Asynchronous signatures endpoint group."""

    async def list(self, document_id: str) -> list[SignatureDetail]:
        validate_id(document_id, "document_id")
        data = await self._request("GET", f"/api/v2/documents/{document_id}/signatures")
        return [SignatureDetail.model_validate(s) for s in cast(list[Any], data)]

    async def add(self, document_id: str, *, signature: str, stamp: str | None = None) -> None:
        validate_id(document_id, "document_id")
        body: dict[str, Any] = {"signature": signature}
        if stamp is not None:
            body["stamp"] = stamp
        await self._request("POST", f"/api/v2/documents/{document_id}/signatures", json=body)

    async def flows(self, document_id: str) -> list[FlowEntry]:
        validate_id(document_id, "document_id")
        data = await self._request("GET", f"/api/v2/documents/{document_id}/flows")
        return [FlowEntry.model_validate(f) for f in cast(list[Any], data)]
