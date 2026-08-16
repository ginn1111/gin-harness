---
status: completed
size: S
scope: Ginflow Kanban observability guidance
owner: ginb
---

# Brief — GINFLOW-10 Watch working cards with `/background`

## Objective

Guide an interactive Hermes agent to launch a read-only `/background` watcher when starting or resuming a selected working Kanban card, then report only meaningful status changes.

## Scope

- `skills/ginflow/SKILL.md`
- `skills/ginflow/references/kanban-guide.md` when detailed policy is needed
- Deterministic Ginflow guidance tests
- This brief

## Acceptance criteria

- [x] Interactive startup guidance uses `/background <prompt>` for the explicitly selected task ID.
- [x] The watcher is read-only and cannot claim, edit, complete, block, dispatch, or otherwise mutate cards or the workspace.
- [x] It reports `completed`, `blocked`, `failed`, `reclaimed/retried`, and materially stalled work.
- [x] Routine heartbeats, unchanged status, and historical events replayed at watcher startup are suppressed.
- [x] Each report is evidence-based and concise, including task ID, current state, and meaningful reason or result.
- [x] The watcher exits after a terminal state and does not create duplicate watchers for the same task.
- [x] Non-interactive surfaces use a documented read-only process watcher fallback rather than pretending `/background` was invoked.
- [x] `make lint` and `make test` pass.

## Watcher prompt contract

The `/background` prompt must:

1. Pin one explicit Kanban task ID and board.
2. Record the initial event boundary before watching.
3. Ignore events at or before that boundary.
4. Poll/read only; never mutate Kanban or repository state.
5. Suppress heartbeat-only and unchanged-state updates.
6. Return only on meaningful transition or a defined material-stall threshold.
7. Stop permanently on `done`, `archived`, or another terminal outcome.

## Non-goals

- Implement a new Hermes slash command.
- Replace Kanban events, dispatcher heartbeats, or gateway notifications.
- Run a second implementation agent in the same workspace.

## Dependency

Queued behind active same-workspace card `t_a6b72183`; no parallel mutation is allowed.

## Verification

Canonical commands: `make lint` and `make test`.
