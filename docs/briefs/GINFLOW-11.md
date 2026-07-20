---
status: ready
size: S
scope: Ginflow worker baseline commits
owner: gintary
---

# Brief — GINFLOW-11 Workers auto-commit artifact baselines

## Objective

Allow Ginflow Kanban workers to create required baseline commits before atomic card completion, removing human review wait while preserving baseline and verification gates.

## Scope

- Ginflow lifecycle and drift-detection guidance.
- Ginflow gate/harness regression coverage.
- `plugins/ginflow-gate/`, `skills/ginflow/`, and `docs/briefs/GINFLOW-11.md`.

## Acceptance criteria

- [ ] Worker guidance permits committing exact linked target-local artifacts before first `kanban_complete` call.
- [ ] Completion still rejects missing, mismatched, unavailable, or drifted artifact baselines.
- [ ] `make test` passes.

## Non-goals

- Broader Git permission changes outside Ginflow worker lifecycle.
- Human approval removal for completed-card drift resolution.

## Notes

Canonical verification: `make test`.
