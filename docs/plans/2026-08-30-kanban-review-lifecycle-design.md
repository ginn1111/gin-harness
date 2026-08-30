---
status: completed
size: M
scope: Canonical Kanban review lifecycle architecture and repo-doc alignment
owner: ginb
---

# Plan — canonical Kanban review lifecycle alignment

## Goal

Align gin-harness canonical architecture and repo-level documentation to Hermes-owned Kanban review lifecycle without adding lifecycle state machinery to Ginflow.

## Decisions

1. Hermes Kanban owns lifecycle state transitions.
   - Worker submits completed governed work with `kanban_request_review`.
   - Reviewer approves with `kanban_complete`.
   - Reviewer rejects with `kanban_request_changes`.
2. Ginflow skill guides workers and reviewers.
3. `ginflow-gate` validates Ginflow-specific evidence at native transition points; it does not implement or duplicate review lifecycle state.
4. Rejection handoff stays minimal: `reason`, `evidence`, `next_action`.

## Evidence-first execution

1. Read current card, local rules, README, architecture docs, Draw.io source, and current plugin guidance.
2. Confirm current stale surfaces.
   - Existing flow showed `Can complete?` and `Make card as review` on canonical diagram/derived doc.
   - Repo prose described completion only as worker `kanban_complete` path.
3. Update canonical diagram page `Gin-harness system` to show Hermes-owned review path.
4. Update derived Markdown and repo docs to match diagram and ownership boundary.
5. Keep scope read-only for Hermes runtime contracts; do not modify Hermes core.
6. Run `make lint` and `make test`.

## Non-goals

- Hermes core lifecycle implementation changes.
- New Ginflow lifecycle state machine.
- Changes outside listed card scope.

## Acceptance mapping

- Diagram shows `running -> review -> done` and review rejection back to worker rework.
- Docs state: Hermes Kanban owns transitions, Ginflow guides agents, `ginflow-gate` validates transitions.
- Rejection handoff limited to `reason`, `evidence`, `next_action`.
- Repo-level prose removes stale worker-direct completion guidance.
