"""Roles / employees endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from vchasno._sync.endpoints._base import SyncEndpoint
from vchasno._utils import UNSET as _UNSET
from vchasno._utils import _Unset, collect_update, validate_id
from vchasno.models.roles import RoleList


class SyncRoles(SyncEndpoint):
    """Asynchronous roles endpoint group."""

    def list(self) -> RoleList:
        data = self._request("GET", "/api/v2/roles")
        return RoleList.model_validate(data)

    def update(
        self,
        role_id: str,
        *,
        # Identity
        user_role: int | None | _Unset = _UNSET,
        position: str | None | _Unset = _UNSET,
        status: str | None | _Unset = _UNSET,
        # IP restrictions
        allowed_ips: list[str] | None | _Unset = _UNSET,
        allowed_api_ips: list[str] | None | _Unset = _UNSET,
        # Document permissions
        can_view_document: bool | _Unset = _UNSET,
        can_view_private_document: bool | _Unset = _UNSET,
        can_comment_document: bool | _Unset = _UNSET,
        can_upload_document: bool | _Unset = _UNSET,
        can_download_document: bool | _Unset = _UNSET,
        can_print_document: bool | _Unset = _UNSET,
        can_delete_document: bool | _Unset = _UNSET,
        can_sign_and_reject_document: bool | _Unset = _UNSET,
        can_remove_itself_from_approval: bool | _Unset = _UNSET,
        # Management permissions
        can_edit_company: bool | _Unset = _UNSET,
        can_edit_roles: bool | _Unset = _UNSET,
        can_invite_coworkers: bool | _Unset = _UNSET,
        can_edit_document_templates: bool | _Unset = _UNSET,
        can_edit_document_fields: bool | _Unset = _UNSET,
        can_edit_templates: bool | _Unset = _UNSET,
        can_archive_documents: bool | _Unset = _UNSET,
        can_delete_archived_documents: bool | _Unset = _UNSET,
        can_create_tags: bool | _Unset = _UNSET,
        can_edit_directories: bool | _Unset = _UNSET,
        can_edit_required_fields: bool | _Unset = _UNSET,
        can_download_actions: bool | _Unset = _UNSET,
        can_edit_company_contact: bool | _Unset = _UNSET,
        can_edit_security: bool | _Unset = _UNSET,
        can_change_document_signers_and_reviewers: bool | _Unset = _UNSET,
        can_delete_document_extended: bool | _Unset = _UNSET,
        can_edit_document_category: bool | _Unset = _UNSET,
        can_view_coworkers: bool | _Unset = _UNSET,
        # Notifications
        can_receive_inbox: bool | _Unset = _UNSET,
        can_receive_inbox_as_default: bool | _Unset = _UNSET,
        can_receive_comments: bool | _Unset = _UNSET,
        can_receive_rejects: bool | _Unset = _UNSET,
        can_receive_reviews: bool | _Unset = _UNSET,
        can_receive_reminders: bool | _Unset = _UNSET,
        can_receive_access_to_doc: bool | _Unset = _UNSET,
        can_receive_delete_requests: bool | _Unset = _UNSET,
        can_receive_review_process_finished: bool | _Unset = _UNSET,
        can_receive_review_process_finished_assigner: bool | _Unset = _UNSET,
        can_receive_sign_process_finished: bool | _Unset = _UNSET,
        can_receive_sign_process_finished_assigner: bool | _Unset = _UNSET,
        can_receive_finished_docs: bool | _Unset = _UNSET,
        can_receive_new_roles: bool | _Unset = _UNSET,
        can_receive_token_expiration: bool | _Unset = _UNSET,
        can_receive_email_change: bool | _Unset = _UNSET,
        can_receive_admin_role_deletion: bool | _Unset = _UNSET,
        # Display
        show_child_documents: bool | _Unset = _UNSET,
    ) -> None:
        validate_id(role_id, "role_id")
        body = collect_update(
            # Identity
            user_role=user_role,
            position=position,
            status=status,
            # IP restrictions
            allowed_ips=allowed_ips,
            allowed_api_ips=allowed_api_ips,
            # Document permissions
            can_view_document=can_view_document,
            can_view_private_document=can_view_private_document,
            can_comment_document=can_comment_document,
            can_upload_document=can_upload_document,
            can_download_document=can_download_document,
            can_print_document=can_print_document,
            can_delete_document=can_delete_document,
            can_sign_and_reject_document=can_sign_and_reject_document,
            can_remove_itself_from_approval=can_remove_itself_from_approval,
            # Management permissions
            can_edit_company=can_edit_company,
            can_edit_roles=can_edit_roles,
            can_invite_coworkers=can_invite_coworkers,
            can_edit_document_templates=can_edit_document_templates,
            can_edit_document_fields=can_edit_document_fields,
            can_edit_templates=can_edit_templates,
            can_archive_documents=can_archive_documents,
            can_delete_archived_documents=can_delete_archived_documents,
            can_create_tags=can_create_tags,
            can_edit_directories=can_edit_directories,
            can_edit_required_fields=can_edit_required_fields,
            can_download_actions=can_download_actions,
            can_edit_company_contact=can_edit_company_contact,
            can_edit_security=can_edit_security,
            can_change_document_signers_and_reviewers=can_change_document_signers_and_reviewers,
            can_delete_document_extended=can_delete_document_extended,
            can_edit_document_category=can_edit_document_category,
            can_view_coworkers=can_view_coworkers,
            # Notifications
            can_receive_inbox=can_receive_inbox,
            can_receive_inbox_as_default=can_receive_inbox_as_default,
            can_receive_comments=can_receive_comments,
            can_receive_rejects=can_receive_rejects,
            can_receive_reviews=can_receive_reviews,
            can_receive_reminders=can_receive_reminders,
            can_receive_access_to_doc=can_receive_access_to_doc,
            can_receive_delete_requests=can_receive_delete_requests,
            can_receive_review_process_finished=can_receive_review_process_finished,
            can_receive_review_process_finished_assigner=can_receive_review_process_finished_assigner,
            can_receive_sign_process_finished=can_receive_sign_process_finished,
            can_receive_sign_process_finished_assigner=can_receive_sign_process_finished_assigner,
            can_receive_finished_docs=can_receive_finished_docs,
            can_receive_new_roles=can_receive_new_roles,
            can_receive_token_expiration=can_receive_token_expiration,
            can_receive_email_change=can_receive_email_change,
            can_receive_admin_role_deletion=can_receive_admin_role_deletion,
            # Display
            show_child_documents=show_child_documents,
        )
        self._request("PATCH", f"/api/v2/roles/{role_id}", json=body)

    def delete(self, role_id: str) -> None:
        validate_id(role_id, "role_id")
        self._request("DELETE", f"/api/v2/roles/{role_id}")

    def invite_coworkers(self, *, emails: Sequence[str]) -> None:
        self._request("POST", "/api/v2/invite/coworkers", json={"emails": list(emails)})

    def create_coworker(
        self,
        *,
        email: str,
        first_name: str | None = None,
        second_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
    ) -> None:
        body: dict[str, Any] = {"email": email}
        if first_name is not None:
            body["first_name"] = first_name
        if second_name is not None:
            body["second_name"] = second_name
        if last_name is not None:
            body["last_name"] = last_name
        if phone is not None:
            body["phone"] = phone
        self._request("POST", "/api/v2/coworker", json=body)

    def create_tokens(self, *, emails: Sequence[str], expire_days: str | None = None) -> None:
        body: dict[str, Any] = {"emails": list(emails)}
        if expire_days is not None:
            body["expire_days"] = expire_days
        self._request("POST", "/api/v2/tokens", json=body)

    def delete_tokens(self, *, emails: Sequence[str]) -> None:
        self._request("DELETE", "/api/v2/tokens", json={"emails": list(emails)})
