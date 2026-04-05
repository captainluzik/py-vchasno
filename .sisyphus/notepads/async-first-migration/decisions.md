# Decisions — Async-First Migration

## Task 1: Tool Selection

**Decision:** Use `unasyncd` (not `unasync`) for async→sync code generation.

**Rationale:**
- `unasyncd` uses libcst (CST-based), handles multi-token transforms like `asyncio.sleep()`
- `unasync` is token-based, cannot handle `asyncio.sleep()` or `httpx.AsyncClient`
- `unasyncd` has `--ruff-fix`/`--ruff-format` integration
- Used by elasticsearch-py, psycopg3

**CI Strategy:** `unasyncd --force && git diff --exit-code` (not `--check`)
