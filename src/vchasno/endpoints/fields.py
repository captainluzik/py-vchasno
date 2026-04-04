"""Custom fields endpoints."""

from __future__ import annotations

from typing import Any

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.common import CustomField, DocumentField


class SyncFields(SyncEndpoint):
    """Synchronous fields endpoint group."""

    def list(self) -> list[CustomField]:
        """GET /api/v2/fields."""
        data = self._request("GET", "/api/v2/fields")
        return [CustomField.model_validate(f) for f in data]

    def create(self, *, name: str, field_type: str, is_required: bool = False) -> CustomField:
        """POST /api/v2/fields."""
        data = self._request("POST", "/api/v2/fields", json={"name": name, "field_type": field_type, "is_required": is_required})
        return CustomField.model_validate(data)

    def list_for_document(self, document_id: str) -> list[DocumentField]:
        """GET /api/v2/documents/{id}/fields."""
        data = self._request("GET", f"/api/v2/documents/{document_id}/fields")
        return [DocumentField.model_validate(f) for f in data]

    def add_to_document(self, document_id: str, *, field_id: str, value: str, is_required: bool = False) -> Any:
        """POST /api/v2/documents/{id}/fields."""
        return self._request("POST", f"/api/v2/documents/{document_id}/fields", json={"field_id": field_id, "value": value, "is_required": is_required})


class AsyncFields(AsyncEndpoint):
    """Asynchronous fields endpoint group."""

    async def list(self) -> list[CustomField]:
        data = await self._request("GET", "/api/v2/fields")
        return [CustomField.model_validate(f) for f in data]

    async def create(self, *, name: str, field_type: str, is_required: bool = False) -> CustomField:
        data = await self._request("POST", "/api/v2/fields", json={"name": name, "field_type": field_type, "is_required": is_required})
        return CustomField.model_validate(data)

    async def list_for_document(self, document_id: str) -> list[DocumentField]:
        data = await self._request("GET", f"/api/v2/documents/{document_id}/fields")
        return [DocumentField.model_validate(f) for f in data]

    async def add_to_document(self, document_id: str, *, field_id: str, value: str, is_required: bool = False) -> Any:
        return await self._request("POST", f"/api/v2/documents/{document_id}/fields", json={"field_id": field_id, "value": value, "is_required": is_required})
