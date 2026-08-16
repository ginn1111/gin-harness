---
status: completed
size: S
scope: ginflow-gate routing
owner: ginb
---

# Brief — GINFLOW-7 Status-based routing

## Objective

Implement deterministic, fail-closed routing for Kanban cards associated with the current workspace.

## Scope

- `plugins/ginflow-gate/routing.py`
- `plugins/ginflow-gate/test_ginflow_gate.py`
- This brief

## Acceptance criteria

- [x] Multiple workspace matches return `needs_card_selection` and require orchestrator selection.
- [x] An explicitly selected task from another workspace returns `workspace_mismatch`.
- [x] A blocked card returns `blocked_card`.
- [x] No matching card returns the canonical no-card route.
- [x] Terminal, invalid, and validation-failure states return deterministic safe routes.
- [x] Routing regression tests pass.
- [x] `make lint` and `make test` pass.

## Non-goals

- Automatic card selection.
- Workspace switching.
- Hermes core status or claim changes.

## Provenance

Replacement for malformed card `t_d243ba13`, created with explicit human approval.

## Verification

Canonical commands: `make lint` and `make test`.

---
**Status: completed** — linked card `t_841e072f` is done.
