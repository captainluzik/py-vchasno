"""Reports endpoints."""

from __future__ import annotations

from vchasno.endpoints._base import AsyncEndpoint, SyncEndpoint
from vchasno.models.common import ReportRequest, ReportStatus


class SyncReports(SyncEndpoint):
    """Synchronous reports endpoint group."""

    def request_document_actions(self, *, date_from: str, date_to: str) -> ReportRequest:
        """POST /api/v2/document-actions/request-report."""
        data = self._request("POST", "/api/v2/document-actions/request-report", json={"date_from": date_from, "date_to": date_to})
        return ReportRequest.model_validate(data)

    def request_user_actions(self, *, date_from: str, date_to: str) -> ReportRequest:
        """POST /api/v2/user-actions/request-report."""
        data = self._request("POST", "/api/v2/user-actions/request-report", json={"date_from": date_from, "date_to": date_to})
        return ReportRequest.model_validate(data)

    def status(self, report_id: str) -> ReportStatus:
        """GET /api/v2/actions/report-status/{id}."""
        data = self._request("GET", f"/api/v2/actions/report-status/{report_id}")
        return ReportStatus.model_validate(data)

    def download(self, report_id: str) -> bytes:
        """GET /api/v2/actions/download-report/{id}."""
        return self._request("GET", f"/api/v2/actions/download-report/{report_id}")


class AsyncReports(AsyncEndpoint):
    """Asynchronous reports endpoint group."""

    async def request_document_actions(self, *, date_from: str, date_to: str) -> ReportRequest:
        data = await self._request("POST", "/api/v2/document-actions/request-report", json={"date_from": date_from, "date_to": date_to})
        return ReportRequest.model_validate(data)

    async def request_user_actions(self, *, date_from: str, date_to: str) -> ReportRequest:
        data = await self._request("POST", "/api/v2/user-actions/request-report", json={"date_from": date_from, "date_to": date_to})
        return ReportRequest.model_validate(data)

    async def status(self, report_id: str) -> ReportStatus:
        data = await self._request("GET", f"/api/v2/actions/report-status/{report_id}")
        return ReportStatus.model_validate(data)

    async def download(self, report_id: str) -> bytes:
        return await self._request("GET", f"/api/v2/actions/download-report/{report_id}")
