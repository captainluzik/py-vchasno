"""Signatures endpoints."""

from __future__ import annotations

from typing import Any

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.documents import FlowEntry, SignatureDetail


class SyncSignatures(SyncEndpoint):
    """Synchronous signatures endpoint group."""

    def list(self, document_id: str) -> list[SignatureDetail]:
        """GET /api/v2/documents/{id}/signatures."""
        data = self._request("GET", f"/api/v2/documents/{document_id}/signatures")
        return [SignatureDetail.model_validate(s) for s in data]

    def add(self, document_id: str, *, signature: str, stamp: str | None = None) -> Any:
        """POST /api/v2/documents/{id}/signatures."""
        body: dict[str, Any] = {"signature": signature}
        if stamp is not None:
            body["stamp"] = stamp
        return self._request("POST", f"/api/v2/documents/{document_id}/signatures", json=body)

    def flows(self, document_id: str) -> list[FlowEntry]:
        """GET /api/v2/documents/{id}/flows."""
        data = self._request("GET", f"/api/v2/documents/{document_id}/flows")
        return [FlowEntry.model_validate(f) for f in data]


class AsyncSignatures(AsyncEndpoint):
    """Asynchronous signatures endpoint group."""

    async def list(self, document_id: str) -> list[SignatureDetail]:
        data = await self._request("GET", f"/api/v2/documents/{document_id}/signatures")
        return [SignatureDetail.model_validate(s) for s in data]

    async def add(self, document_id: str, *, signature: str, stamp: str | None = None) -> Any:
        body: dict[str, Any] = {"signature": signature}
        if stamp is not None:
            body["stamp"] = stamp
        return await self._request("POST", f"/api/v2/documents/{document_id}/signatures", json=body)

    async def flows(self, document_id: str) -> list[FlowEntry]:
        data = await self._request("GET", f"/api/v2/documents/{document_id}/flows")
        return [FlowEntry.model_validate(f) for f in data]
