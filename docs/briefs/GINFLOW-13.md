---
status: ready
size: S
scope: Linked-artifact worktree repair guidance
owner: gintary
---

# Brief — GINFLOW-13 Document linked-artifact worktree repairs

## Objective

Document safe repair when a Ginflow linked brief or artifact is missing from assigned worktree.

## Scope

- `docs/briefs/GINFLOW-13.md`
- `docs/guides/ginflow-linked-artifact-repair.md`
- No profile runtime state, cron jobs, Kanban implementation, or product repositories.

## Acceptance criteria

- [ ] Guide gives restore/create, scoped commit, harness, and unblock order.
- [ ] Guide prevents simultaneous active cards in same mutable workspace.
- [ ] Guide prohibits silent completion-baseline advancement.
- [ ] `make test` passes.
- [ ] `make lint` passes.

## Non-goals

- Repairing any specific card.
- Editing task bodies or changing Kanban lifecycle behavior.

## Notes

Canonical verification: `make test`; documentation lint: `make lint`.
