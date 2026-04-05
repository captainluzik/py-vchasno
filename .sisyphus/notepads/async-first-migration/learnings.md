# Learnings — Async-First Migration

## Task 1: unasyncd PoC

### unasyncd automatic transformations (built-in)
- `async def` → `def`
- `await expr` → `expr`
- `asyncio.sleep()` → `time.sleep()` (adds `import time`)
- `__aenter__` → `__enter__`
- `__aexit__` → `__exit__`

### Requires `add_replacements` config
- `AsyncClient` → `Client` (httpx-specific, NOT `SyncClient`)
- `aclose` → `close` (httpx-specific asymmetry)
- All project class names: `AsyncTransport` → `SyncTransport`, etc.

### --check mode quirk
- Reliably detects MISSING sync files
- Does NOT reliably detect content drift in existing files
- CI workaround: `unasyncd --force && git diff --exit-code -- <sync files>`

### unasyncd leaves stale `import asyncio`
- After transforming `asyncio.sleep` → `time.sleep`, the `import asyncio` remains
- Use `--ruff-fix` flag or separate `ruff --fix` to clean up

### unasyncd does not transform docstrings by default
- `--transform-docstrings` flag exists but needs testing
