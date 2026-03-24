# AGENTS.md

## Purpose
- Guide AI coding agents working on this repo's single-file Python SDK for Arkham Intel API (`arkham_client.py`).
- Keep changes aligned with the public API surface documented in `README.md` and `openapi.json`.

## Read First (in order)
- `arkham_client.py`: all runtime behavior, auth flow, request plumbing, and endpoint wrappers.
- `README.md`: canonical usage patterns, parameter examples, rate-limit and billing caveats.
- `openapi.json`: source-of-truth endpoint/parameter definitions for API v1.1.0.
- `llms-full.md`: extended domain/API semantics (entity-first model, auth, streaming guidance).

## Big-Picture Architecture
- The SDK is intentionally thin: one `ArkhamClient` class wraps `requests.Session` and exposes endpoint-specific convenience methods.
- Data flow is: user method -> `_clean(...)` params -> `get/post/put/delete` -> `_ensure_login()` -> `requests.Session` call -> `.json()` response.
- Authentication has two modes:
  - API key mode: set `API-Key` header at init and mark client logged-in immediately.
  - Email/password mode: first API call triggers `login()` which calls `LOGIN_URL` then exchanges `tradeInToken` at `AUTH_URL`.
- URL handling is centralized in `_url`; pass either relative API paths (normal) or absolute URLs (supported).

## Project-Specific Conventions
- Preserve method naming by endpoint family (`intelligence_*`, `token_*`, `ws_*`, `user_*`, etc.); this is the discoverability pattern in `README.md`.
- Always build query params with `_clean(...)`; it removes `None`, lowercases bools (`True` -> `"true"`), and maps Python-safe `from_` -> `from`.
- Keep wrappers thin: each method should map directly to one endpoint path and return `response.json()`.
- Respect existing compatibility aliases: `address_balances`, `address_transfers`, `address_intelligence`.
- Do not add hidden retries/backoff or custom error swallowing in core methods; HTTP errors currently propagate via `raise_for_status()` only in `login()`.

## Adding or Updating Endpoints
- Derive path + params from `openapi.json`, then mirror the style used in neighboring methods.
- Prefer explicit typed arguments for common params and `**kwargs` only where endpoints are filter-heavy (for example `transfers`, `swaps`, `counterparties_*`).
- Add/update README examples when public method names or signatures change.
- If a field name conflicts with Python keywords, follow the existing underscore convention (`from_`, not `from`).

## Developer Workflow (this repo)
- Install dependency:
  - `pip install requests`
- Basic syntax check used in this repo:
  - `python3 -m py_compile arkham_client.py`
- Quick manual smoke test pattern (requires credentials): instantiate `ArkhamClient`, call `chains()` or `intelligence_address(...)` as shown in `README.md`.

## Guardrails for Agent Changes
- This repo has no formal test suite/config; avoid broad refactors unless explicitly requested.
- Keep docs and code in sync: if behavior changes in `arkham_client.py`, update `README.md` in the same change.
- Preserve ASCII-only edits unless a file already uses non-ASCII (current docs include Chinese text; code should stay plain ASCII where possible).

