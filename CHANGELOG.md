# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.1]: https://github.com/captainluzik/py-vchasno/releases/tag/v0.1.1
[0.1.0]: https://github.com/captainluzik/py-vchasno/releases/tag/v0.1.0
