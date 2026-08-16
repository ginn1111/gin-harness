---
status: completed
size: S
scope: bounded blocked-card recovery policy
owner: ginb
---

# Brief — GINFLOW-17 Implement bounded recovery policy

## Objective

Implement a pure, fail-closed policy that decides whether the orchestrator may retry a blocked card by assigning it to the recorded previous worker.

## Scope

- `plugins/ginflow-gate/recovery_policy.py`
- `plugins/ginflow-gate/test_recovery_policy.py`
- Canonical `Makefile` test wiring
- This brief

## Acceptance criteria

- [x] Only valid `blocked` events for the selected card and canonical workspace are evaluated.
- [x] `transient` and `unknown` blockers retry the recorded previous worker below three attempts.
- [x] Attempt three yields deterministic `notify_human` while the card remains blocked.
- [x] Non-recoverable, malformed, mismatched, terminal, and non-blocked states never reassign.
- [x] Previously processed idempotency keys are skipped.
- [x] Evaluation is pure and does not mutate metadata or Kanban state.
- [x] Focused tests, `make lint`, and `make test` pass.

## Non-goals

- Lease or concurrency storage
- Cron scheduling and scanning
- Telegram delivery
- Direct Kanban mutation

## Verification

Canonical commands: `make lint` and `make test`.
