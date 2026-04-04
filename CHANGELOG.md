# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/captainluzik/py-vchasno/releases/tag/v0.1.0
