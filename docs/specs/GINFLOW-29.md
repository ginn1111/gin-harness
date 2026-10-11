---
status: in_progress
scope:
  - plugins/ginflow-gate/ block routing for transient kind and test
owner: ginb
---

# GINFLOW-29 — Repairable block routes to gintary

Refs: ginn1111/gin-harness#26 (parent spec), #30 (this slice). Shared contract: `docs/specs/GINFLOW-26.md` (B1 to B8) and issue #26.

## Objective

With trace on, a `transient` worker block is annotated as worker-origin, assigned to `gintary`, and unblocked.

## Contract

- A `transient` block **must** write a bounded card comment marking `origin=worker` with worker profile, run ID, kind and sanitized reason.
- The task **must** be assigned to `gintary` and unblocked.
- With trace off, native behavior **must** be unchanged.

## Acceptance criteria

- [ ] `transient` block writes the origin comment with profile, run ID, kind, reason
- [ ] Task assigned to `gintary` and unblocked
- [ ] Trace off: native behavior, no assignment
- [ ] `make lint && make test` pass
