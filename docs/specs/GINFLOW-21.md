---
status: in_progress
size: M
scope: Standalone opt-in tracing package for Ginflow plugin function calls
owner: ginb
---
# Spec — GINFLOW-21 Ginflow trace logging

## Objective

Provide an independent `ginflow-trace` plugin package that records Ginflow plugin function calls for worker debugging without changing plugin behavior.

## Contract

Tracing is disabled unless `GINFLOW_LOG=1`. When enabled, decorated functions append JSON events to `plugins/ginflow-trace/logs/`. Each file represents one session-worker/Kanban-worker pair and contains a JSON list. The filename is `<session_worker_id>__<kanban_worker_id>.json`; if either identity is unknown, append a UUID suffix only for that fallback case.

Identity resolution uses hook context first and then `HERMES_SESSION_WORKER_ID` / `HERMES_KANBAN_TASK`. Missing values are represented as `unknown` in the filename and the generated UUID prevents collisions.

Each event records a UTC RFC3339 timestamp, the bare function name, sanitized/truncated input and output, and status. Sensitive keys are redacted. Function exceptions are recorded under `errors/` and then re-raised. Trace/storage errors never block or alter the wrapped plugin function.

## Scope

- `plugins/ginflow-trace/` package, decorator, identity resolver, sanitizer, atomic JSON storage, and tests.
- Decorator integration for Ginflow gate business functions and hook entry points.

## Non-goals

- No default file logging.
- No raw secrets, cookies, authorization values, or full traceback persistence.
- No changes to Kanban behavior or gate decisions.

## Verification

Run `make lint`, the focused tracing test, and `make test`.

**Status: completed**
