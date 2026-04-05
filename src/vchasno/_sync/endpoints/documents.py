"""Documents endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO, cast

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno._utils import UNSET as _UNSET
from vchasno._utils import _Unset, collect_params, collect_update
from vchasno.models.common import UpdatedIds
from vchasno.models.documents import (
    Document,
    DocumentList,
    DocumentStatusList,
    DownloadDocumentList,
    IncomingDocumentList,
    StructuredData,
)


class SyncDocuments(SyncEndpoint):
    """Asynchronous documents endpoint group."""

    # -- list / get -----------------------------------------------------

    def list(
        self,
        *,
        status: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        category: int | None = None,
        edrpou: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        search: str | None = None,
        tag_id: str | None = None,
        is_archived: bool | None = None,
        sd_status: str | None = None,
        **extra: Any,
    ) -> DocumentList:
        params = collect_params(
            status=status,
            cursor=cursor,
            limit=limit,
            category=category,
            edrpou=edrpou,
            date_from=date_from,
            date_to=date_to,
            search=search,
            tag_id=tag_id,
            is_archived=is_archived,
            sd_status=sd_status,
            **extra,
        )
        data = self._request("GET", "/api/v2/documents", params=params or None)
        return DocumentList.model_validate(data)

    def get(self, document_id: str) -> Document:
        data = self._request("GET", f"/api/v2/documents/{document_id}")
        if isinstance(data, dict) and "documents" in data:
            return Document.model_validate(data["documents"][0])
        return Document.model_validate(data)

    # -- upload / update ------------------------------------------------

    def upload(
        self,
        file: str | Path | BinaryIO,
        *,
        filename: str | None = None,
        category: int | None = None,
        recipient_edrpou: str | None = None,
        edrpou: str | None = None,
        email: str | None = None,
        title: str | None = None,
        **extra: Any,
    ) -> DocumentList:
        """Upload a document.

        Args:
            file: Path or file object to upload.
            filename: Override the filename sent in multipart form-data.
            category: Document category ID.
            recipient_edrpou: Recipient EDRPOU code.
            edrpou: **Deprecated** — use *recipient_edrpou* instead.
            email: Recipient email.
            title: Document title.
            **extra: Additional query parameters forwarded to the API.
        """
        resolved_edrpou = recipient_edrpou or edrpou
        opened: BinaryIO | None = None
        if isinstance(file, (str, Path)):
            path = Path(file)
            filename = filename or path.name
            opened = fp = open(path, "rb")
        else:
            fp = file
            filename = filename or "document"
        try:
            files = [("file", (filename, fp))]
            query = collect_params(
                category=category,
                edrpou=resolved_edrpou,
                email=email,
                title=title,
                **extra,
            )
            data = self._request("POST", "/api/v2/documents", params=query or None, files=files)
        finally:
            if opened is not None:
                opened.close()
        if isinstance(data, dict) and "documents" in data:
            return DocumentList.model_validate(data)
        return DocumentList(documents=[Document.model_validate(data)])

    def update_info(
        self,
        document_id: str,
        *,
        title: str | None | _Unset = _UNSET,
        number: str | None | _Unset = _UNSET,
        date: str | None | _Unset = _UNSET,
        amount: int | None | _Unset = _UNSET,
        category: int | None | _Unset = _UNSET,
        first_sign_by: str | None | _Unset = _UNSET,
        **extra: Any,
    ) -> Document:
        body = collect_update(
            title=title,
            number=number,
            date=date,
            amount=amount,
            category=category,
            first_sign_by=first_sign_by,
        )
        body.update(extra)
        data = self._request("PATCH", f"/api/v2/documents/{document_id}/info", json=body)
        return Document.model_validate(data)

    def update_recipient(self, document_id: str, *, edrpou: str, email: str) -> None:
        self._request(
            "PATCH", f"/api/v2/documents/{document_id}/recipient", json={"edrpou": edrpou, "email": email}
        )

    def update_access_settings(self, document_id: str, *, level: str) -> None:
        self._request("PATCH", f"/api/v2/documents/{document_id}/access-settings", json={"level": level})

    def update_viewers(
        self,
        document_id: str,
        *,
        strategy: str,
        groups_ids: list[str] | None = None,
        roles_ids: list[str] | None = None,
    ) -> None:
        body: dict[str, Any] = {"strategy": strategy}
        if groups_ids is not None:
            body["groups_ids"] = groups_ids
        if roles_ids is not None:
            body["roles_ids"] = roles_ids
        self._request("PATCH", f"/api/v2/documents/{document_id}/viewers-settings", json=body)

    # -- flow / signers -------------------------------------------------

    def set_flow(self, document_id: str, flow: list[dict[str, Any]]) -> None:
        self._request("POST", f"/api/v2/documents/{document_id}/flow", json=flow)

    def set_signers(
        self, document_id: str, *, signer_entities: list[dict[str, str]], is_parallel: bool = True
    ) -> None:
        self._request(
            "POST",
            f"/api/v2/documents/{document_id}/signers",
            json={"signer_entities": signer_entities, "is_parallel": is_parallel},
        )

    # -- incoming -------------------------------------------------------

    def list_incoming(
        self,
        *,
        status: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        category: int | None = None,
        edrpou: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        search: str | None = None,
        tag_id: str | None = None,
        is_archived: bool | None = None,
        sd_status: str | None = None,
        **extra: Any,
    ) -> IncomingDocumentList:
        params = collect_params(
            status=status,
            cursor=cursor,
            limit=limit,
            category=category,
            edrpou=edrpou,
            date_from=date_from,
            date_to=date_to,
            search=search,
            tag_id=tag_id,
            is_archived=is_archived,
            sd_status=sd_status,
            **extra,
        )
        data = self._request("GET", "/api/v2/incoming-documents", params=params or None)
        return IncomingDocumentList.model_validate(data)

    # -- downloads ------------------------------------------------------

    def download_original(self, document_id: str, *, version: str | None = None) -> bytes:
        params = {"version": version} if version is not None else None
        return cast(bytes, self._request("GET", f"/api/v2/documents/{document_id}/original", params=params))

    def download_archive(self, document_id: str, *, with_instruction: int | None = None) -> bytes:
        params = {"with_instruction": with_instruction} if with_instruction is not None else None
        return cast(bytes, self._request("GET", f"/api/v2/documents/{document_id}/archive", params=params))

    def download_p7s(self, document_id: str) -> bytes:
        return cast(bytes, self._request("GET", f"/api/v2/documents/{document_id}/p7s"))

    def download_asic(self, document_id: str) -> bytes:
        return cast(bytes, self._request("GET", f"/api/v2/documents/{document_id}/asic"))

    def download_documents(self, ids: list[str]) -> DownloadDocumentList:
        params = [("ids", i) for i in ids]
        data = self._request("GET", "/api/v2/download-documents", params=params)
        return DownloadDocumentList.model_validate(data)

    # -- conversion / print ---------------------------------------------

    def xml_to_pdf_create(self, document_id: str, *, force: bool = False) -> None:
        self._request("POST", f"/api/v2/documents/{document_id}/xml-to-pdf", json={"force": force})

    def xml_to_pdf_download(self, document_id: str) -> bytes:
        return cast(bytes, self._request("GET", f"/api/v2/documents/{document_id}/xml-to-pdf"))

    def pdf_print(self, document_id: str) -> bytes:
        return cast(bytes, self._request("GET", f"/api/v2/documents/{document_id}/pdf/print"))

    # -- status / actions -----------------------------------------------

    def statuses(self, document_ids: list[str]) -> DocumentStatusList:
        if len(document_ids) > 500:
            raise ValueError("Maximum 500 document IDs per request")
        data = self._request("POST", "/api/v2/documents/statuses", json={"document_ids": document_ids})
        return DocumentStatusList.model_validate(data)

    def reject(self, document_id: str, *, text: str) -> None:
        self._request("POST", f"/api/v2/documents/{document_id}/reject", json={"text": text})

    def send(self, document_id: str) -> None:
        self._request("POST", f"/api/v2/documents/{document_id}/send")

    def delete(self, document_id: str) -> None:
        self._request("DELETE", f"/api/v2/documents/{document_id}")

    def archive(self, document_ids: list[str], *, directory_id: str | None = None) -> None:
        body: dict[str, Any] = {"document_ids": document_ids}
        if directory_id is not None:
            body["directory_id"] = directory_id
        self._request("POST", "/api/v2/documents/archive", json=body)

    def unarchive(self, document_ids: list[str]) -> None:
        self._request("DELETE", "/api/v2/documents/archive", json={"document_ids": document_ids})

    def mark_as_processed(self, document_ids: list[str]) -> UpdatedIds:
        data = self._request("POST", "/api/v2/documents/mark-as-processed", json={"document_ids": document_ids})
        return UpdatedIds.model_validate(data)

    def structured_data_download(
        self, document_id: str, *, output_format: str = "json"
    ) -> StructuredData | bytes:
        data = self._request(
            "GET", f"/api/v2/documents/{document_id}/structured-data/download", params={"format": output_format}
        )
        if isinstance(data, bytes):
            return data
        return StructuredData.model_validate(data)
