"""Documents endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import IO, Any, cast

from vchasno._async._pagination import AsyncCursorPage
from vchasno._async.endpoints._base import AsyncEndpoint
from vchasno._files import open_file
from vchasno._utils import UNSET as _UNSET
from vchasno._utils import _Unset, collect_params, collect_update, validate_id
from vchasno.models.common import UpdatedIds
from vchasno.models.documents import (
    Document,
    DocumentList,
    DocumentStatusList,
    DownloadDocumentList,
    FlowEntryInput,
    IncomingDocument,
    SignerEntityInput,
    StructuredData,
)
from vchasno.models.enums import (
    AccessSettingsLevel,
    DocumentCategory,
    DocumentStatus,
    FirstSignBy,
    ReviewState,
    StructuredDataStatus,
    ViewersStrategy,
)


class AsyncDocuments(AsyncEndpoint):
    """Asynchronous documents endpoint group."""

    # -- list / get -----------------------------------------------------

    async def list(
        self,
        *,
        status: int | DocumentStatus | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        category: int | DocumentCategory | None = None,
        edrpou: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        date_rejected_from: str | None = None,
        date_rejected_to: str | None = None,
        date_document_from: str | None = None,
        date_document_to: str | None = None,
        date_finished_from: str | None = None,
        date_finished_to: str | None = None,
        search: str | None = None,
        tag_id: str | None = None,
        is_archived: bool | None = None,
        sd_status: str | StructuredDataStatus | None = None,
        extension: str | None = None,
        recipient_edrpou: str | None = None,
        number: str | None = None,
        vendor: str | None = None,
        vendor_id: str | None = None,
        ids: list[str] | None = None,
        has_changed: bool | None = None,
        is_delivered: bool | None = None,
        is_internal: bool | None = None,
        with_tags: bool | None = None,
        not_tagged: bool | None = None,
        with_recipients: bool | None = None,
        with_connections: bool | None = None,
        amount_eq: int | None = None,
        amount_gte: int | None = None,
        amount_lte: int | None = None,
        with_document_fields: bool | None = None,
        with_versions: bool | None = None,
        with_delete_requests: bool | None = None,
        with_access_settings: bool | None = None,
        review_state: str | ReviewState | None = None,
        date_review_approved_from: str | None = None,
        date_review_approved_to: str | None = None,
        **extra: Any,
    ) -> AsyncCursorPage[Document]:
        params = collect_params(
            status=status,
            cursor=cursor,
            limit=limit,
            category=category,
            edrpou=edrpou,
            date_from=date_from,
            date_to=date_to,
            date_rejected_from=date_rejected_from,
            date_rejected_to=date_rejected_to,
            date_document_from=date_document_from,
            date_document_to=date_document_to,
            date_finished_from=date_finished_from,
            date_finished_to=date_finished_to,
            search=search,
            tag_id=tag_id,
            is_archived=is_archived,
            sd_status=sd_status,
            extension=extension,
            recipient_edrpou=recipient_edrpou,
            number=number,
            vendor=vendor,
            vendor_id=vendor_id,
            has_changed=has_changed,
            is_delivered=is_delivered,
            is_internal=is_internal,
            with_tags=with_tags,
            not_tagged=not_tagged,
            with_recipients=with_recipients,
            with_connections=with_connections,
            amount_eq=amount_eq,
            amount_gte=amount_gte,
            amount_lte=amount_lte,
            with_document_fields=with_document_fields,
            with_versions=with_versions,
            with_delete_requests=with_delete_requests,
            with_access_settings=with_access_settings,
            review_state=review_state,
            date_review_approved_from=date_review_approved_from,
            date_review_approved_to=date_review_approved_to,
            **extra,
        )
        _multi: list[tuple[str, Any]] = []
        if ids is not None:
            _multi.extend(("ids", v) for v in ids)
        if _multi:
            data = await self._request("GET", "/api/v2/documents", params=list(params.items()) + _multi)
        else:
            data = await self._request("GET", "/api/v2/documents", params=params or None)
        return AsyncCursorPage._from_response(
            cast(dict[str, Any], data),
            model_cls=Document,
            transport=self._t,
            path="/api/v2/documents",
            params=params or {},
            data_key="documents",
        )

    async def get(self, document_id: str) -> Document:
        validate_id(document_id, "document_id")
        data = await self._request("GET", f"/api/v2/documents/{document_id}")
        if isinstance(data, dict) and "documents" in data:
            return Document.model_validate(data["documents"][0])
        return Document.model_validate(data)

    # -- upload / update ------------------------------------------------

    async def upload(
        self,
        file: str | Path | IO[bytes],
        *,
        filename: str | None = None,
        category: int | DocumentCategory | None = None,
        recipient_edrpou: str | None = None,
        edrpou: str | None = None,
        email: str | None = None,
        title: str | None = None,
        expected_owner_signatures: int | None = None,
        expected_recipient_signatures: int | None = None,
        first_sign_by: str | FirstSignBy | None = None,
        signer_roles: list[str] | None = None,
        signer_emails: list[str] | None = None,
        parallel_signing: bool | None = None,
        is_internal: bool | None = None,
        is_multilateral: bool | None = None,
        is_parallel: bool | None = None,
        share_to: list[str] | None = None,
        share_to_groups: list[str] | None = None,
        reviewers_ids: list[str] | None = None,
        reviewers_emails: list[str] | None = None,
        parallel_review: bool | None = None,
        is_required_review: bool | None = None,
        tags: list[str] | None = None,
        parent_id: str | None = None,
        doc_number: str | None = None,
        date_document: str | None = None,
        amount: int | None = None,
        is_versioned: bool | None = None,
        template_id: str | None = None,
        show_recipients: bool | None = None,
        with_access_settings: bool | None = None,
        access_settings_level: str | AccessSettingsLevel | None = None,
        recipient_emails: list[str] | None = None,
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
            expected_owner_signatures: Number of expected owner signatures.
            expected_recipient_signatures: Number of expected recipient signatures.
            first_sign_by: Who signs first (``"owner"`` or ``"recipient"``).
            signer_roles: Role IDs for signers (multi-value).
            signer_emails: Signer emails (multi-value).
            parallel_signing: Enable parallel signing.
            is_internal: Mark as internal document.
            is_multilateral: Mark as multilateral document.
            is_parallel: Enable parallel flow.
            share_to: Role IDs to share document with (multi-value).
            share_to_groups: Group IDs to share document with (multi-value).
            reviewers_ids: Reviewer role IDs (multi-value).
            reviewers_emails: Reviewer emails (multi-value).
            parallel_review: Enable parallel review.
            is_required_review: Make review required before signing.
            tags: Tag names to assign (multi-value).
            parent_id: Parent document ID for linking.
            doc_number: Document number.
            date_document: Document date (``YYYY-MM-DD``).
            amount: Amount in kopecks.
            is_versioned: Enable versioning.
            template_id: Template ID for structured data.
            show_recipients: Show recipients list.
            with_access_settings: Include access settings in response.
            access_settings_level: Access settings level.
            recipient_emails: Recipient emails (multi-value).
            **extra: Additional query parameters forwarded to the API.
        """
        resolved_edrpou = recipient_edrpou or edrpou
        with open_file(file, filename=filename) as (resolved_name, fp):
            files = [("file", (resolved_name, fp))]
            query = collect_params(
                category=category,
                edrpou=resolved_edrpou,
                email=email,
                title=title,
                expected_owner_signatures=expected_owner_signatures,
                expected_recipient_signatures=expected_recipient_signatures,
                first_sign_by=first_sign_by,
                parallel_signing=parallel_signing,
                is_internal=is_internal,
                is_multilateral=is_multilateral,
                is_parallel=is_parallel,
                parallel_review=parallel_review,
                is_required_review=is_required_review,
                parent_id=parent_id,
                doc_number=doc_number,
                date_document=date_document,
                amount=amount,
                is_versioned=is_versioned,
                template_id=template_id,
                show_recipients=show_recipients,
                with_access_settings=with_access_settings,
                access_settings_level=access_settings_level,
                **extra,
            )
            _multi: list[tuple[str, Any]] = []
            _mv: list[tuple[str, list[str] | None]] = [
                ("signer_roles", signer_roles),
                ("signer_emails", signer_emails),
                ("share_to", share_to),
                ("share_to_groups", share_to_groups),
                ("reviewers_ids", reviewers_ids),
                ("reviewers_emails", reviewers_emails),
                ("tags", tags),
                ("recipient_emails", recipient_emails),
            ]
            for _name, _values in _mv:
                if _values is not None:
                    _multi.extend((_name, v) for v in _values)
            if _multi:
                data = await self._request(
                    "POST",
                    "/api/v2/documents",
                    params=list(query.items()) + _multi,
                    files=files,
                )
            else:
                data = await self._request("POST", "/api/v2/documents", params=query or None, files=files)
        if isinstance(data, dict) and "documents" in data:
            return DocumentList.model_validate(data)
        return DocumentList(documents=[Document.model_validate(data)])

    async def update_info(
        self,
        document_id: str,
        *,
        title: str | None | _Unset = _UNSET,
        number: str | None | _Unset = _UNSET,
        date: str | None | _Unset = _UNSET,
        amount: int | None | _Unset = _UNSET,
        category: int | DocumentCategory | None | _Unset = _UNSET,
        first_sign_by: str | FirstSignBy | None | _Unset = _UNSET,
        validate: bool = True,
        **extra: Any,
    ) -> Document:
        validate_id(document_id, "document_id")
        if validate:
            doc = await self.get(document_id)
            from vchasno._state import validate_document_state

            validate_document_state(doc.status, "update_info")
        body = collect_update(
            title=title,
            number=number,
            date=date,
            amount=amount,
            category=category,
            first_sign_by=first_sign_by,
        )
        body.update(extra)
        data = await self._request("PATCH", f"/api/v2/documents/{document_id}/info", json=body)
        return Document.model_validate(data)

    async def update_recipient(self, document_id: str, *, edrpou: str, email: str, validate: bool = True) -> None:
        validate_id(document_id, "document_id")
        if validate:
            doc = await self.get(document_id)
            from vchasno._state import validate_document_state

            validate_document_state(doc.status, "update_recipient")
        await self._request(
            "PATCH", f"/api/v2/documents/{document_id}/recipient", json={"edrpou": edrpou, "email": email}
        )

    async def update_access_settings(self, document_id: str, *, level: str | AccessSettingsLevel) -> None:
        validate_id(document_id, "document_id")
        await self._request("PATCH", f"/api/v2/documents/{document_id}/access-settings", json={"level": level})

    async def update_viewers(
        self,
        document_id: str,
        *,
        strategy: str | ViewersStrategy,
        groups_ids: Sequence[str] | None = None,
        roles_ids: Sequence[str] | None = None,
    ) -> None:
        validate_id(document_id, "document_id")
        body: dict[str, Any] = {"strategy": strategy}
        if groups_ids is not None:
            body["groups_ids"] = list(groups_ids)
        if roles_ids is not None:
            body["roles_ids"] = list(roles_ids)
        await self._request("PATCH", f"/api/v2/documents/{document_id}/viewers-settings", json=body)

    # -- flow / signers -------------------------------------------------

    async def set_flow(
        self, document_id: str, flow: Sequence[dict[str, Any] | FlowEntryInput], *, validate: bool = True
    ) -> None:
        validate_id(document_id, "document_id")
        if validate:
            doc = await self.get(document_id)
            from vchasno._state import validate_document_state

            validate_document_state(doc.status, "set_flow")
        payload = [entry.model_dump() if isinstance(entry, FlowEntryInput) else entry for entry in flow]
        await self._request("POST", f"/api/v2/documents/{document_id}/flow", json=payload)

    async def set_signers(
        self,
        document_id: str,
        *,
        signer_entities: Sequence[dict[str, str] | SignerEntityInput],
        is_parallel: bool = True,
        validate: bool = True,
    ) -> None:
        validate_id(document_id, "document_id")
        if validate:
            doc = await self.get(document_id)
            from vchasno._state import validate_document_state

            validate_document_state(doc.status, "set_signers")
        payload = [entry.model_dump() if isinstance(entry, SignerEntityInput) else entry for entry in signer_entities]
        await self._request(
            "POST",
            f"/api/v2/documents/{document_id}/signers",
            json={"signer_entities": payload, "is_parallel": is_parallel},
        )

    # -- incoming -------------------------------------------------------

    async def list_incoming(
        self,
        *,
        status: int | DocumentStatus | None = None,
        cursor: str | None = None,
        category: int | DocumentCategory | None = None,
        date_created_from: str | None = None,
        date_created_to: str | None = None,
        date_sent_from: str | None = None,
        date_sent_to: str | None = None,
        date_document_from: str | None = None,
        date_document_to: str | None = None,
        date_finished_from: str | None = None,
        date_finished_to: str | None = None,
        edrpou_owner: str | None = None,
        extension: str | None = None,
        ids: list[str] | None = None,
        with_recipients: bool | None = None,
        with_connections: bool | None = None,
        tag_id: str | None = None,
        not_tagged: bool | None = None,
        amount_eq: int | None = None,
        amount_gte: int | None = None,
        amount_lte: int | None = None,
        with_document_fields: bool | None = None,
        with_versions: bool | None = None,
        processed: bool | None = None,
        with_delete_requests: bool | None = None,
        with_access_settings: bool | None = None,
        is_archived: bool | None = None,
        review_state: str | ReviewState | None = None,
        date_review_approved_from: str | None = None,
        date_review_approved_to: str | None = None,
        sd_status: str | StructuredDataStatus | None = None,
        **extra: Any,
    ) -> AsyncCursorPage[IncomingDocument]:
        params = collect_params(
            status=status,
            cursor=cursor,
            category=category,
            date_created_from=date_created_from,
            date_created_to=date_created_to,
            date_sent_from=date_sent_from,
            date_sent_to=date_sent_to,
            date_document_from=date_document_from,
            date_document_to=date_document_to,
            date_finished_from=date_finished_from,
            date_finished_to=date_finished_to,
            edrpou_owner=edrpou_owner,
            extension=extension,
            with_recipients=with_recipients,
            with_connections=with_connections,
            tag_id=tag_id,
            not_tagged=not_tagged,
            amount_eq=amount_eq,
            amount_gte=amount_gte,
            amount_lte=amount_lte,
            with_document_fields=with_document_fields,
            with_versions=with_versions,
            processed=processed,
            with_delete_requests=with_delete_requests,
            with_access_settings=with_access_settings,
            is_archived=is_archived,
            review_state=review_state,
            date_review_approved_from=date_review_approved_from,
            date_review_approved_to=date_review_approved_to,
            sd_status=sd_status,
            **extra,
        )
        _multi: list[tuple[str, Any]] = []
        if ids is not None:
            _multi.extend(("ids", v) for v in ids)
        if _multi:
            data = await self._request("GET", "/api/v2/incoming-documents", params=list(params.items()) + _multi)
        else:
            data = await self._request("GET", "/api/v2/incoming-documents", params=params or None)
        return AsyncCursorPage._from_response(
            cast(dict[str, Any], data),
            model_cls=IncomingDocument,
            transport=self._t,
            path="/api/v2/incoming-documents",
            params=params or {},
            data_key="documents",
        )

    # -- downloads ------------------------------------------------------

    async def download_original(self, document_id: str, *, version: str | None = None) -> bytes:
        validate_id(document_id, "document_id")
        params = {"version": version} if version is not None else None
        return cast(bytes, await self._request("GET", f"/api/v2/documents/{document_id}/original", params=params))

    async def download_archive(
        self,
        document_id: str,
        *,
        with_instruction: int | None = None,
        with_xml_preview: bool | None = None,
        convert_to_signature_format: str | None = None,
        filenames_max_length: int | None = None,
    ) -> bytes:
        validate_id(document_id, "document_id")
        if filenames_max_length is not None and not (10 <= filenames_max_length <= 255):
            raise ValueError("filenames_max_length must be between 10 and 255")
        params = collect_params(
            with_instruction=with_instruction,
            with_xml_preview=with_xml_preview,
            convert_to_signature_format=convert_to_signature_format,
            filenames_max_length=filenames_max_length,
        )
        return cast(
            bytes, await self._request("GET", f"/api/v2/documents/{document_id}/archive", params=params or None)
        )

    async def download_p7s(self, document_id: str) -> bytes:
        validate_id(document_id, "document_id")
        return cast(bytes, await self._request("GET", f"/api/v2/documents/{document_id}/p7s"))

    async def download_asic(self, document_id: str) -> bytes:
        validate_id(document_id, "document_id")
        return cast(bytes, await self._request("GET", f"/api/v2/documents/{document_id}/asic"))

    async def download_documents(self, ids: Sequence[str]) -> DownloadDocumentList:
        params = [("ids", i) for i in ids]
        data = await self._request("GET", "/api/v2/download-documents", params=params)
        return DownloadDocumentList.model_validate(data)

    # -- conversion / print ---------------------------------------------

    async def xml_to_pdf_create(self, document_id: str, *, force: bool = False) -> None:
        validate_id(document_id, "document_id")
        await self._request("POST", f"/api/v2/documents/{document_id}/xml-to-pdf", json={"force": force})

    async def xml_to_pdf_download(self, document_id: str) -> bytes:
        validate_id(document_id, "document_id")
        return cast(bytes, await self._request("GET", f"/api/v2/documents/{document_id}/xml-to-pdf"))

    async def pdf_print(self, document_id: str) -> bytes:
        validate_id(document_id, "document_id")
        return cast(bytes, await self._request("GET", f"/api/v2/documents/{document_id}/pdf/print"))

    # -- status / actions -----------------------------------------------

    async def statuses(self, document_ids: Sequence[str]) -> DocumentStatusList:
        if len(document_ids) > 500:
            raise ValueError("Maximum 500 document IDs per request")
        data = await self._request("POST", "/api/v2/documents/statuses", json={"document_ids": list(document_ids)})
        return DocumentStatusList.model_validate(data)

    async def reject(self, document_id: str, *, text: str, validate: bool = True) -> None:
        validate_id(document_id, "document_id")
        if validate:
            doc = await self.get(document_id)
            from vchasno._state import validate_document_state

            validate_document_state(doc.status, "reject")
        await self._request("POST", f"/api/v2/documents/{document_id}/reject", json={"text": text})

    async def send(self, document_id: str, *, validate: bool = True) -> None:
        validate_id(document_id, "document_id")
        if validate:
            doc = await self.get(document_id)
            from vchasno._state import validate_document_state

            validate_document_state(doc.status, "send")
        await self._request("POST", f"/api/v2/documents/{document_id}/send")

    async def delete(self, document_id: str, *, validate: bool = True) -> None:
        validate_id(document_id, "document_id")
        if validate:
            doc = await self.get(document_id)
            from vchasno._state import validate_document_state

            validate_document_state(doc.status, "delete")
        await self._request("DELETE", f"/api/v2/documents/{document_id}")

    async def archive(self, document_ids: Sequence[str], *, directory_id: str | None = None) -> None:
        body: dict[str, Any] = {"document_ids": list(document_ids)}
        if directory_id is not None:
            body["directory_id"] = directory_id
        await self._request("POST", "/api/v2/documents/archive", json=body)

    async def unarchive(self, document_ids: Sequence[str]) -> None:
        await self._request("DELETE", "/api/v2/documents/archive", json={"document_ids": list(document_ids)})

    async def mark_as_processed(self, document_ids: Sequence[str]) -> UpdatedIds:
        data = await self._request(
            "POST", "/api/v2/documents/mark-as-processed", json={"document_ids": list(document_ids)}
        )
        return UpdatedIds.model_validate(data)

    async def structured_data_download(
        self, document_id: str, *, output_format: str = "json"
    ) -> StructuredData | bytes:
        validate_id(document_id, "document_id")
        data = await self._request(
            "GET", f"/api/v2/documents/{document_id}/structured-data/download", params={"format": output_format}
        )
        if isinstance(data, bytes):
            return data
        return StructuredData.model_validate(data)
