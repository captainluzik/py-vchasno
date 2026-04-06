# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-04-05

### Breaking Changes

- **Package restructure**: async-first architecture with `unasyncd`. Sync code auto-generated.
  - Import paths changed: `vchasno._async.*` for async, `vchasno._sync.*` for sync
  - Top-level imports (`from vchasno import Vchasno, AsyncVchasno`) unchanged
- `create_sign_session`: parameter `type` renamed to `session_type` to avoid shadowing Python builtin
- Methods that return no meaningful data now return `None` instead of raw response dict:
  `set_flow`, `set_signers`, `reject`, `send`, `delete`, `archive`, `unarchive`, and others

### Added

- **Transport hardening**: automatic retry on network errors (`httpx.TransportError`, `httpx.TimeoutException`)
- **Full jitter** in exponential backoff (prevents thundering herd)
- **HTTPS enforcement**: `base_url` must use HTTPS (pass `allow_http=True` to override for testing)
- **Retry-After cap**: capped at 60 seconds to prevent indefinite blocking
- **HTTP-Date format** support in `Retry-After` header (RFC 7231)
- **Streaming downloads**: `request_stream` context manager for large files
- `download_archive`: new `with_instruction` parameter
- `upload`: new `recipient_edrpou` parameter (explicit, replaces ambiguous `edrpou`)
- `statuses`: client-side validation — rejects >500 document IDs
- `validate_id`: path parameter sanitization to prevent URL path injection
- `collect_update`: preserves `None` for PATCH endpoints (clearing fields)
- `_files.py` and `_utils.py`: shared utilities for file handling and parameter collection
- `__repr__` on transport classes masks API token
- `extra="allow"` on all Pydantic API response models (forward compatibility)

### Fixed

- Exception messages truncated to 500 chars (full body in `response_body` attribute)
- `AuthenticationError` docstring: now correctly states "401/403"
- JSON parsing: malformed JSON raises `VchasnoError` instead of `JSONDecodeError`
- Empty JSON body with `application/json` content-type returns `None` instead of crash
- `StructuredData` model: `dict[str, object]` → `dict[str, Any]`
- Removed global `disable_error_code` from mypy (per-line ignores instead)

### Changed

- All `-> Any` public methods replaced with proper return types (`-> None`, models, or `dict[str, Any]`)
- `_UNSET` sentinel: proper `_Unset` enum type instead of `Any = object()`
- Expanded ruff rules: added `A`, `C4`, `T20`, `RUF`
- `unasyncd` added to dev dependencies

## [0.1.1] - 2026-04-05

### Fixed

- **Falsy-value bug**: replaced all `if value:` checks with `if value is not None:` across endpoint files — empty strings and zero values are no longer silently dropped.
- **Python 3.10 compatibility**: `Self` type import moved under `TYPE_CHECKING` guard.
- **File handle safety**: `open()` calls are now always inside `try/finally` to prevent resource leaks on errors.
- **PyPI token exposure**: release workflow now uses environment variables instead of CLI arguments for `twine` credentials.

### Changed

- **HTTP retry**: now retries on 502, 503, 504 in addition to 429; honours `Retry-After` header when present.
- **401 Unauthorized**: mapped to `AuthenticationError` alongside 403.
- **Structured logging**: all HTTP requests and retries are logged via `logging.getLogger("vchasno")`.
- **Model deduplication**: `Document` and `IncomingDocument` now inherit from a shared `_BaseDocument` base class.
- **Typed dict fields**: `dict` / `list[dict]` fields replaced with proper Pydantic models — `StampInfo`, `Author`, `CategoryDetails`, `AccessSettings`, `TagRef`, `FieldRef`, `DeleteRequestRef`, `ArchiveScanDocument`, and Template settings models.
- **Typed API parameters**: `documents.list()`, `list_incoming()`, `upload()`, `update_info()`, `comments.list()`, and `delete_requests.list()` now have explicit keyword parameters instead of `**kwargs`.
- `delete_requests.list()` returns `list[DeleteRequestRef]` instead of `list[dict]`.
- `structured_data_download()` parameter renamed from `format` to `output_format` to avoid shadowing the builtin.
- `CustomField.order` type changed from `str` to `int`.
- `_base.py` params type broadened to accept `list[tuple[str, Any]]` for multi-value query parameters.

### Added

- `__version__` attribute on the `vchasno` package.
- `vchasno.models` now re-exports all models and enums for convenient access.
- CI workflow (`.github/workflows/ci.yml`) running pytest, ruff, and mypy on Python 3.10–3.13.
- `[project.optional-dependencies] dev` section in `pyproject.toml` (pytest, pytest-asyncio, mypy, ruff).
- `asyncio_mode = "auto"` in pytest configuration.
- New tests for 401 error handling, 5xx retry, and `Retry-After` header.

## [0.1.0] - 2026-04-04

### Added

- Initial release of the Vchasno.EDO API v2 Python SDK.
- `Vchasno` (sync) and `AsyncVchasno` (async) client classes.
- Full coverage of 19 API endpoint groups:
  - Documents (list, upload, download, edit, reject, send, archive, statuses, structured data)
  - Signatures (list, add, flows)
  - Comments (list, add)
  - Reviews / approval (history, requests, status, add/remove reviewer)
  - Versions (upload, delete)
  - Delete requests (create, cancel, accept, reject, lock/unlock)
  - Tags (CRUD for documents and roles)
  - Archive (directories, scans, import signed external/internal)
  - Categories (CRUD)
  - Custom fields (CRUD, document fields)
  - Child documents (add, remove)
  - Groups / teams (CRUD, members)
  - Roles / employees (list, update, delete, invite, tokens)
  - Templates / scenarios (list, get)
  - Reports (request, status, download)
  - Cloud signer / Vchasno.KEP (sessions, sign, refresh tokens)
  - Billing (activate trial)
  - Company check (single, bulk upload)
  - Sign sessions (view/sign session for personal cabinet)
- Pydantic v2 models for all API responses.
- Enums for document statuses (7000-7011), categories (0-18891), review states, etc.
- Automatic retry with exponential backoff on HTTP 429 (rate limit).
- `py.typed` marker for type checker support.
- Typed exception hierarchy: `VchasnoError` > `VchasnoAPIError` > `Auth/RateLimit/NotFound/BadRequest`.

[0.2.0]: https://github.com/captainluzik/py-vchasno/releases/tag/v0.2.0
[0.1.1]: https://github.com/captainluzik/py-vchasno/releases/tag/v0.1.1
[0.1.0]: https://github.com/captainluzik/py-vchasno/releases/tag/v0.1.0
