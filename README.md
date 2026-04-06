# py-vchasno

> **Disclaimer:** This is an **unofficial** SDK, not affiliated with or endorsed by Vchasno.
> It was built based on publicly available information about the Vchasno.EDO API v2.

[![PyPI version](https://img.shields.io/pypi/v/py-vchasno.svg)](https://pypi.org/project/py-vchasno/)
[![Python 3.10+](https://img.shields.io/pypi/pyversions/py-vchasno.svg)](https://pypi.org/project/py-vchasno/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python SDK for [Vchasno.EDO](https://edo.vchasno.ua) API v2 — Ukrainian electronic document management service.

## Features

- **Sync & Async** clients — `Vchasno` and `AsyncVchasno` (async-first with `unasyncd`)
- **Full API coverage** — all 19 endpoint groups (documents, signatures, comments, reviews, tags, archive, cloud signer, etc.)
- **Auto-pagination** — `CursorPage` supports direct iteration over all pages
- **Cloud Signer helpers** — `sign_and_wait()` for automatic polling and signing
- **State Validation** — SDK validates document state before operations (FSM)
- **Transport hardening** — automatic retry on network errors and `429` with full jitter exponential backoff
- **HTTPS enforcement** — secure by default (transport-level `allow_http=True` for testing)
- **Streaming downloads** — `request_stream` context manager for large files
- **Pydantic v2** models with full type annotations and `extra="allow"` for forward compatibility
- **`py.typed`** — first-class support for mypy / pyright

## Installation

### pip

```bash
pip install py-vchasno
```

### uv

```bash
uv add py-vchasno
```

### poetry

```bash
poetry add py-vchasno
```

### From source

```bash
git clone https://github.com/captainluzik/py-vchasno.git
cd py-vchasno
pip install .
```

## Quick start

### Sync client

```python
from vchasno import Vchasno
from vchasno.models import DocumentStatus

client = Vchasno(token="your-token")

# List documents with typed enums
page = client.documents.list(status=DocumentStatus.FULLY_SIGNED)
for doc in page.data:
    print(doc.id, doc.title)

# Auto-pagination
for doc in client.documents.list(status=DocumentStatus.UPLOADED):
    print(doc.id)  # iterates ALL pages automatically

# Upload with full configuration
docs = client.documents.upload(
    "contract.pdf",
    recipient_edrpou="12345678",
    expected_owner_signatures=2,
    first_sign_by="owner",
    template_id="tmpl-1",
)

# Cloud signing with automatic polling
client.cloud_signer.sign_and_wait(
    document_id=doc.id,
    client_id="cloud-key-id",
    password="key-password",
    timeout=120.0,
)

client.close()
```

### Async client

```python
import asyncio
from vchasno import AsyncVchasno
from vchasno.models import DocumentStatus

async def main():
    async with AsyncVchasno(token="your-token") as client:
        # Auto-pagination works in async too
        async for doc in client.documents.list(status=DocumentStatus.FULLY_SIGNED):
            print(doc.id)

        # Cloud signing
        await client.cloud_signer.sign_and_wait(
            document_id="doc-id",
            client_id="cloud-key-id",
            password="key-password",
        )

asyncio.run(main())
```

## Authentication

Generate an API token in [Vchasno.EDO settings](https://edo.vchasno.ua). The token is sent as `Authorization: <token>` header.

```python
client = Vchasno(token="your-api-token")
```

The `base_url` must use HTTPS (default: `https://edo.vchasno.ua`).

Optionally override the base URL and timeout:

```python
client = Vchasno(
    token="your-api-token",
    base_url="https://edo.vchasno.ua",  # default; HTTPS required
    timeout=60.0,                        # seconds, default 30
    max_retries=5,                       # retry on 429 / network errors, default 3
)
```

## Custom httpx Client

Ви можете використовувати власний `httpx.Client` або `httpx.AsyncClient` для налаштування проксі, сертифікатів або інших параметрів транспорту.

```python
import httpx
from vchasno import Vchasno

custom = httpx.Client(proxy="http://proxy:8080")
client = Vchasno(token="tok", http_client=custom)
```

## State Validation

SDK автоматично перевіряє стан документа перед виконанням операцій (наприклад, чи можна відправити документ у поточному статусі).

```python
# SDK validates document state before operations
client.documents.send(doc_id)  # raises DocumentStateError if status doesn't allow send

# Disable validation for performance
client.documents.send(doc_id, validate=False)
```

## API reference

All endpoints are accessible as attributes of the client object. Each group provides both sync and async versions.

### Documents — `client.documents`

```python
# List outgoing documents with filters
page = client.documents.list(
    status=DocumentStatus.FULLY_SIGNED,
    date_from="2024-01-01",
    date_to="2024-12-31",
)

# Access items via .data
for doc in page.data:
    print(doc.id)

# Manual pagination with cursor
page = client.documents.list()
if page.next_cursor:
    next_page = client.documents.list(cursor=page.next_cursor)

# Get single document
doc = client.documents.get("document-uuid")

# Upload (multipart/form-data)
result = client.documents.upload(
    "contract.pdf",
    recipient_edrpou="12345678",
    recipient_emails="recipient@company.com",
    category=3,
    amount=1500000,  # amount in kopecks (= 15000.00 UAH)
    first_sign_by="owner",
)

# Upload from file object
with open("doc.pdf", "rb") as f:
    result = client.documents.upload(f, filename="doc.pdf")

# Edit document metadata (status < 7003)
client.documents.update_info(
    "document-uuid",
    title="Updated title",
    amount=500000,
    category=1,
)

# Edit recipient
client.documents.update_recipient("document-uuid", edrpou="87654321", email="new@mail.com")

# Access settings
client.documents.update_access_settings("document-uuid", level="private")
client.documents.update_viewers("document-uuid", strategy="add", roles_ids=["role-uuid"])

# Set multilateral signers
client.documents.set_flow("document-uuid", [
    {"edrpou": "11111111", "emails": ["signer@a.com"], "order": 0, "sign_num": 1},
    {"edrpou": "22222222", "emails": ["signer@b.com"], "order": 1, "sign_num": 1},
])

# List incoming documents
incoming = client.documents.list_incoming(
    status=DocumentStatus.READY_TO_SIGN,
    date_created_from="2024-01-01",
)

# Set signers for a document
client.documents.set_signers("document-uuid", signer_entities=[
    {"type": "role", "id": "role-uuid"},
    {"type": "group", "id": "group-uuid"},
], is_parallel=False)

# Download original file
content = client.documents.download_original("document-uuid")
with open("original.pdf", "wb") as f:
    f.write(content)

# Download specific version
content = client.documents.download_original("document-uuid", version="latest")

# Download ZIP archive with signatures
archive = client.documents.download_archive("document-uuid", with_instruction=1)

# Streaming download (large files, avoids loading into memory)
# async: async with client.documents.request_stream("GET", "/path") as stream: ...
# sync equivalent also available

# Download P7S / ASIC containers
p7s = client.documents.download_p7s("document-uuid")
asic = client.documents.download_asic("document-uuid")

# Batch download info
info = client.documents.download_documents(["uuid-1", "uuid-2"])

# XML to PDF
client.documents.xml_to_pdf_create("document-uuid", force=True)
pdf = client.documents.xml_to_pdf_download("document-uuid")

# PDF print view
printable = client.documents.pdf_print("document-uuid")

# Batch statuses (up to 500 IDs)
statuses = client.documents.statuses(["uuid-1", "uuid-2"])
for s in statuses.data_list:
    print(f"{s.document_id}: {s.status_text}")

# Reject a document
client.documents.reject("document-uuid", text="Incorrect amount")

# Send after signing
client.documents.send("document-uuid")

# Delete
client.documents.delete("document-uuid")

# Archive / unarchive
client.documents.archive(["uuid-1", "uuid-2"], directory_id="dir-uuid")
client.documents.unarchive(["uuid-1", "uuid-2"])

# Mark as processed
result = client.documents.mark_as_processed(["uuid-1", "uuid-2"])

# Structured data (sd_status must be confirmed/downloaded)
sd = client.documents.structured_data_download("document-uuid", output_format="json")
```

### Signatures — `client.signatures`

```python
# List signatures for a document
sigs = client.signatures.list("document-uuid")
for sig in sigs:
    print(f"{sig.signer_name} ({sig.edrpou}) at {sig.timestamp}")

# Add a detached signature (base64-encoded .p7s)
client.signatures.add("document-uuid", signature="base64...", stamp="base64...")

# Multilateral document flows
flows = client.signatures.flows("document-uuid")
```

### Comments — `client.comments`

```python
# All comments across documents
comments = client.comments.list(date_from="2024-01-01")

# Comments for a specific document
doc_comments = client.comments.list_for_document("document-uuid")

# Add a comment
client.comments.add("document-uuid", text="Please review", is_internal=True)
```

### Reviews (Approval) — `client.reviews`

```python
# Approval history
history = client.reviews.history("document-uuid")

# Current review requests
requests = client.reviews.requests("document-uuid")

# Overall status
status = client.reviews.status("document-uuid")
print(f"{status.status}, required={status.is_required}")

# Add / remove reviewer
client.reviews.add_reviewer("document-uuid", user_to_email="reviewer@company.com")
client.reviews.add_reviewer("document-uuid", group_to_name="Accounting", is_parallel=False)
client.reviews.remove_reviewer("document-uuid", user_to_email="reviewer@company.com")
```

### Versions — `client.versions`

```python
# Upload a new version
client.versions.upload("document-uuid", "contract_v2.pdf")

# Delete last version
client.versions.delete("document-uuid", "version-uuid")
```

### Delete Requests — `client.delete_requests`

```python
# Create a delete request
client.delete_requests.create("document-uuid", message="Duplicate document")

# Cancel / accept / reject
client.delete_requests.cancel("document-uuid")
client.delete_requests.accept("document-uuid")
client.delete_requests.reject("document-uuid", reject_message="Not a duplicate")

# List delete requests
requests = client.delete_requests.list(status="new")

# Lock / unlock direct deletion
client.delete_requests.lock_delete(["uuid-1", "uuid-2"])
client.delete_requests.unlock_delete(["uuid-1", "uuid-2"])
```

### Tags — `client.tags`

```python
# List company tags
tags = client.tags.list(limit=100, offset=0)

# Roles linked to a tag
roles = client.tags.roles("tag-uuid")

# Create tags and assign to documents
new_tags = client.tags.create_for_documents(
    documents_ids=["doc-uuid"],
    names=["Urgent", "Q1-2024"],
)

# Connect / disconnect existing tags
client.tags.connect_documents(documents_ids=["doc-uuid"], tags_ids=["tag-uuid"])
client.tags.disconnect_documents(documents_ids=["doc-uuid"], tags_ids=["tag-uuid"])

# Tags for roles (employees)
client.tags.create_for_roles(roles_ids=["role-uuid"], names=["Manager"])
client.tags.connect_roles(roles_ids=["role-uuid"], tags_ids=["tag-uuid"])
client.tags.disconnect_roles(roles_ids=["role-uuid"], tags_ids=["tag-uuid"])
```

### Archive — `client.archive`

```python
# List archive directories
dirs = client.archive.directories(parent_id=None, search="2024")

# Upload scans
result = client.archive.upload_scans(["scan1.pdf", "scan2.pdf"], parent_id=11)

# Import signed document (external format: original + .p7s files)
result = client.archive.import_signed_external(
    "document.pdf",
    ["signature1.p7s", "signature2.p7s"],
    title="Contract",
    amount=1000000,
)

# Import signed document (internal format: .p7s or ASiC-E container)
result = client.archive.import_signed_internal("signed_container.p7s")
```

### Categories — `client.categories`

```python
# List all document categories
cats = client.categories.list()

# Create / update / delete internal category
client.categories.create(title="Custom Type")
client.categories.update(37, title="Renamed Type")
client.categories.delete(37)
```

### Fields — `client.fields`

```python
# List custom fields
fields = client.fields.list()

# Create a new field
field = client.fields.create(name="PO Number", field_type="text", is_required=True)

# Document fields
doc_fields = client.fields.list_for_document("document-uuid")
client.fields.add_to_document("document-uuid", field_id="field-uuid", value="PO-12345")
```

### Children — `client.children`

```python
# Link / unlink child documents
client.children.add("parent-uuid", "child-uuid")
client.children.remove("parent-uuid", "child-uuid")
```

### Groups — `client.groups`

```python
# CRUD groups
groups = client.groups.list()
group = client.groups.create(name="Accounting Team")
client.groups.update("group-uuid", name="Finance Team")
client.groups.delete("group-uuid")

# Members
members = client.groups.members("group-uuid")
client.groups.add_members("group-uuid", role_ids=["role-1", "role-2"])
client.groups.remove_members("group-uuid", group_members=["member-uuid"])
```

### Roles — `client.roles`

```python
# List active employees
roles = client.roles.list()
for r in roles.roles:
    print(f"{r.email} — {r.position}")

# Update permissions / notifications
client.roles.update("role-uuid", can_sign_and_reject_document=True, user_role=8001)

# Invite / create coworkers
client.roles.invite_coworkers(emails=["new@company.com"])
client.roles.create_coworker(email="new@company.com", first_name="John", last_name="Doe")

# Delete employee
client.roles.delete("role-uuid")

# Token management
client.roles.create_tokens(emails=["user@company.com"], expire_days="365")
client.roles.delete_tokens(emails=["user@company.com"])
```

### Templates — `client.templates`

```python
templates = client.templates.list()
template = client.templates.get("template-uuid")
```

### Reports — `client.reports`

```python
# Request a report (max 30-day range)
report = client.reports.request_document_actions(date_from="2024-01-01", date_to="2024-01-31")

# Check status
status = client.reports.status(report.report_id)
if status.status == "ready":
    xlsx = client.reports.download(report.report_id)
    with open(status.filename, "wb") as f:
        f.write(xlsx)

# User actions report
report = client.reports.request_user_actions(date_from="2024-01-01", date_to="2024-01-31")
```

### Cloud Signer (Vchasno.KEP) — `client.cloud_signer`

```python
# Create signing session
session = client.cloud_signer.create_session(duration=3600, client_id="key-uuid")
print(f"Session: {session.auth_session_id}")

# Poll until ready
check = client.cloud_signer.check_session(auth_session_id=session.auth_session_id)
if check.status == "ready":
    token = check.token

# Sign a document
client.cloud_signer.sign_document(
    client_id="key-uuid",
    password="key-password",
    document_id="document-uuid",
    auth_session_token=token,
)

# sign_and_wait() helper (automatic polling)
client.cloud_signer.sign_and_wait(
    document_id="document-uuid",
    client_id="key-uuid",
    password="key-password",
    timeout=120.0,
)
```

### Billing — `client.billing`

```python
# Activate 30-day trial
client.billing.activate_trial()
```

### Company — `client.company`

```python
# Check single counterparty
info = client.company.check(edrpou="12345678")

# Bulk check from .xlsx / .csv
result = client.company.check_upload("counterparties.xlsx")
for c in result.companies:
    print(f"{c.edrpou} {c.name}: {c.is_registered}")
```

## Migration from v0.2

- `documents.list()` тепер повертає `CursorPage[Document]` замість `DocumentList`.
- Доступ до елементів списку через `.data` замість `.documents`.
- Нові виключення: `DocumentStateError`, `CloudSignerError`, `TimeoutError`, `ValidationError`.
- Усі моделі тепер успадковуються від `VchasnoModel`.
- Додано автоматичну пагінацію при ітерації по результату `list()`.

## Enums

The SDK provides enums for all known constants:

```python
from vchasno.models.enums import (
    DocumentStatus,
    DocumentCategory,
    FirstSignBy,
    ReviewState,
    StructuredDataStatus,
    DeleteRequestStatus,
    CloudSignerSessionStatus,
    AccessSettingsLevel,
)

# Document statuses
DocumentStatus.UPLOADED          # 7000
DocumentStatus.READY_TO_SIGN     # 7001
DocumentStatus.FULLY_SIGNED      # 7008
DocumentStatus.ANNULLED          # 7011
```

## Error handling

```python
from vchasno import (
    Vchasno,
    VchasnoError,
    VchasnoAPIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    BadRequestError,
    DocumentStateError,
)

with Vchasno(token="xxx") as client:
    try:
        doc = client.documents.get("non-existent-id")
    except NotFoundError:
        print("Document not found")
    except DocumentStateError as e:
        print(f"Invalid document state: {e}")
    except AuthenticationError:
        print("Invalid or expired token")
    except RateLimitError:
        print("Rate limit exceeded after retries")
    except BadRequestError as e:
        print(f"Bad request: {e.response_body}")
    except VchasnoAPIError as e:
        print(f"API error {e.status_code}: {e}")
    except VchasnoError as e:
        print(f"SDK error: {e}")
```

## Rate limiting

Vchasno API allows 10 requests/second per company. The SDK automatically retries `429` responses and transient network errors (`httpx.TransportError`, `httpx.TimeoutException`) with full jitter exponential backoff. The `Retry-After` header is honoured (capped at 60 s). Configure retries via `max_retries` (default 3).

## Important notes

- **Amounts** are always in **kopecks** (1 UAH = 100 kopecks). Example: `amount=1500000` means 15,000.00 UAH.
- **Datetime** format: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`.
- **File limits**: single file up to 15 MB; ZIP archive up to 500 files / 100 MB.
- **Pagination**: use `cursor` / `next_cursor` pattern for all list endpoints or direct iteration for auto-pagination.

## Development

### Async-First Development

This SDK uses async-first development with [`unasyncd`](https://github.com/provinzkraut/unasyncd).

- Write code in `src/vchasno/_async/` only
- Run `unasyncd` to generate `src/vchasno/_sync/`
- Never edit `_sync/` files manually
- CI verifies sync freshness: `unasyncd --force && git diff --exit-code src/vchasno/_sync/`

### Running checks

```bash
pip install -e ".[dev]"
ruff check src/ tests/
mypy src/
pytest
```

## License

MIT — see [LICENSE](LICENSE).
