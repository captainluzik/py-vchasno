# Task 1: unasyncd PoC Results

**Date:** 2026-04-05
**unasyncd version:** 0.10.0
**Status:** ✅ GATE PASSED — all 9 transformations verified

## Transformation Results

| # | Transformation | Auto | add_replacements | Result |
|---|---|---|---|---|
| 1 | `async def` → `def` | ✅ | — | ✅ PASS |
| 2 | `await expr` → `expr` | ✅ | — | ✅ PASS |
| 3 | `asyncio.sleep(delay)` → `time.sleep(delay)` | ✅ | — | ✅ PASS |
| 4 | `httpx.AsyncClient` → `httpx.Client` | ❌ | `"AsyncClient" = "Client"` | ✅ PASS |
| 5 | `AsyncTransport` → `SyncTransport` | ❌ | `"AsyncTransport" = "SyncTransport"` | ✅ PASS |
| 6 | `AsyncEndpoint` → `SyncEndpoint` | ❌ | `"AsyncEndpoint" = "SyncEndpoint"` | ✅ PASS |
| 7 | `aclose()` → `close()` | ❌ | `"aclose" = "close"` | ✅ PASS |
| 8 | `__aenter__` → `__enter__` | ✅ | — | ✅ PASS |
| 9 | `__aexit__` → `__exit__` | ✅ | — | ✅ PASS |

### Summary
- **5/9 automatic** (built-in to unasyncd): async def, await, asyncio.sleep, __aenter__, __aexit__
- **4/9 via add_replacements**: AsyncClient→Client, AsyncTransport→SyncTransport, AsyncEndpoint→SyncEndpoint, aclose→close
- **0/9 failed**

## Recommended `[tool.unasyncd]` Config for Full Migration

```toml
[tool.unasyncd]
add_replacements = {
    "AsyncTransport" = "SyncTransport",
    "AsyncClient" = "Client",
    "AsyncEndpoint" = "SyncEndpoint",
    "AsyncBilling" = "SyncBilling",
    "AsyncDocuments" = "SyncDocuments",
    "AsyncSignatures" = "SyncSignatures",
    "AsyncComments" = "SyncComments",
    "AsyncReviews" = "SyncReviews",
    "AsyncVersions" = "SyncVersions",
    "AsyncDeleteRequests" = "SyncDeleteRequests",
    "AsyncTags" = "SyncTags",
    "AsyncArchive" = "SyncArchive",
    "AsyncCategories" = "SyncCategories",
    "AsyncFields" = "SyncFields",
    "AsyncChildren" = "SyncChildren",
    "AsyncGroups" = "SyncGroups",
    "AsyncRoles" = "SyncRoles",
    "AsyncTemplates" = "SyncTemplates",
    "AsyncReports" = "SyncReports",
    "AsyncCloudSigner" = "SyncCloudSigner",
    "AsyncCompany" = "SyncCompany",
    "AsyncVchasno" = "Vchasno",
    "aclose" = "close",
}

[tool.unasyncd.files]
# Transport layer
"src/vchasno/_async_http.py" = "src/vchasno/_sync_http.py"
# Base endpoint
"src/vchasno/endpoints/_async_base.py" = "src/vchasno/endpoints/_sync_base.py"
# All endpoint groups (one per file)
"src/vchasno/endpoints/_async/billing.py" = "src/vchasno/endpoints/_sync/billing.py"
# ... etc for all 19 endpoint groups
```

## --check Mode Findings

| Scenario | Exit Code | Works? |
|---|---|---|
| Sync files freshly generated | 0 | ✅ |
| Sync file missing (deleted) | 1 | ✅ |
| Async source modified (content drift) | 0 | ⚠️ Unreliable |
| Sync file tampered (content drift) | 0 | ⚠️ Unreliable |

### --check Limitation

`unasyncd --check` reliably detects **missing** sync files but does **not** reliably detect
**content drift** when both async and sync files exist but are out of sync.

### CI Workaround

For reliable CI enforcement, use the "regen + git diff" pattern:

```bash
unasyncd --force
git diff --exit-code -- src/vchasno/_sync_http.py src/vchasno/endpoints/_sync/
```

If `git diff --exit-code` returns non-zero, sync files are stale.

## Edge Cases Discovered

### 1. Stale `import asyncio` in generated sync files
unasyncd transforms `asyncio.sleep()` → `time.sleep()` and adds `import time`,
but does **not** remove the now-unused `import asyncio`. This leaves a dead import.

**Workaround:** Enable `ruff_fix = true` in config or run `ruff --fix` as post-step.
unasyncd has `--ruff-fix` and `--ruff-format` flags built in.

### 2. Docstrings not transformed by default
Class/method docstrings like `"""Asynchronous HTTP transport"""` are kept as-is.
unasyncd has `--transform-docstrings` flag to enable this, but we should verify
it works correctly before using it in the full migration.

### 3. `import time` placement
unasyncd adds `import time` after all existing imports (line 10, after `import httpx`).
This may violate ruff's import sorting rules.

**Workaround:** `ruff_fix = true` will sort imports correctly.

### 4. `add_replacements` scope
`"aclose" = "close"` replaces ALL occurrences of `aclose` → `close` in the file,
not just method calls. If any variable or string contained "aclose", it would also
be replaced. This is safe for our codebase but worth noting.

Similarly, `"AsyncClient" = "Client"` would replace the name anywhere it appears —
but since we only use it as `httpx.AsyncClient`, this is safe.

## Conclusion

**GATE PASSED.** unasyncd 0.10.0 can correctly transform all critical async patterns
in the py-vchasno SDK into their sync equivalents. The tool is suitable for the
async-first migration strategy.

Recommended next steps:
1. Restructure source layout (async as canonical, sync generated)
2. Configure full `[tool.unasyncd]` with all endpoint groups
3. Enable `--ruff-fix` for import cleanup
4. Use `unasyncd --force && git diff --exit-code` in CI instead of `--check`
