"""Signatures endpoints."""

from __future__ import annotations

from typing import Any, cast

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno._utils import validate_id
from vchasno.models.documents import FlowEntry, SignatureDetail


class SyncSignatures(SyncEndpoint):
    """Asynchronous signatures endpoint group."""

    def list(self, document_id: str) -> list[SignatureDetail]:
        validate_id(document_id, "document_id")
        data = self._request("GET", f"/api/v2/documents/{document_id}/signatures")
        return [SignatureDetail.model_validate(s) for s in cast(list[Any], data)]

    def add(self, document_id: str, *, signature: str, stamp: str | None = None) -> None:
        validate_id(document_id, "document_id")
        body: dict[str, Any] = {"signature": signature}
        if stamp is not None:
            body["stamp"] = stamp
        self._request("POST", f"/api/v2/documents/{document_id}/signatures", json=body)

    def flows(self, document_id: str) -> list[FlowEntry]:
        validate_id(document_id, "document_id")
        data = self._request("GET", f"/api/v2/documents/{document_id}/flows")
        return [FlowEntry.model_validate(f) for f in cast(list[Any], data)]
