---
status: active
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

- [ ] Multiple workspace matches return `needs_card_selection` and require orchestrator selection.
- [ ] An explicitly selected task from another workspace returns `workspace_mismatch`.
- [ ] A blocked card returns `blocked_card`.
- [ ] No matching card returns the canonical no-card route.
- [ ] Terminal, invalid, and validation-failure states return deterministic safe routes.
- [ ] Routing regression tests pass.
- [ ] `make lint` and `make test` pass.

## Non-goals

- Automatic card selection.
- Workspace switching.
- Hermes core status or claim changes.

## Provenance

Replacement for malformed card `t_d243ba13`, created with explicit human approval.

## Verification

Canonical commands: `make lint` and `make test`.
