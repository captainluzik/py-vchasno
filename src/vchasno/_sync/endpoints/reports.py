"""Reports endpoints."""

from __future__ import annotations

from typing import cast

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno.models.common import ReportRequest, ReportStatus


class SyncReports(SyncEndpoint):
    """Asynchronous reports endpoint group."""

    def request_document_actions(self, *, date_from: str, date_to: str) -> ReportRequest:
        data = self._request(
            "POST", "/api/v2/document-actions/request-report", json={"date_from": date_from, "date_to": date_to}
        )
        return ReportRequest.model_validate(data)

    def request_user_actions(self, *, date_from: str, date_to: str) -> ReportRequest:
        data = self._request(
            "POST", "/api/v2/user-actions/request-report", json={"date_from": date_from, "date_to": date_to}
        )
        return ReportRequest.model_validate(data)

    def status(self, report_id: str) -> ReportStatus:
        data = self._request("GET", f"/api/v2/actions/report-status/{report_id}")
        return ReportStatus.model_validate(data)

    def download(self, report_id: str) -> bytes:
        return cast(bytes, self._request("GET", f"/api/v2/actions/download-report/{report_id}"))
