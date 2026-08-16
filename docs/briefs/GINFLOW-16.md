---
status: completed
size: S
scope: worker blocked-card metadata reporting
owner: ginb
---

# Brief — GINFLOW-16 Implement blocked-card metadata reporting

## Objective

Implement worker-side append-only blocker evidence that matches the finalized recovery event contract while keeping all recovery mutations under orchestrator ownership.

## Scope

- `plugins/ginflow-gate/blocker_reporting.py`
- `plugins/ginflow-gate/test_blocker_reporting.py`
- Blocked-route context integration coverage
- Canonical `Makefile` test wiring
- This brief

## Acceptance criteria

- [x] Blocked events contain all required identity, safety, evidence, attempt, decision, and ownership fields.
- [x] Supported blocker kinds are exact and determine `recovery_candidate` deterministically.
- [x] Invalid values fail closed before metadata is emitted.
- [x] Comments use the `[ginflow-recovery] event=...` contract.
- [x] Comments do not expose evidence payloads, commands, secrets, raw logs, or raw PII.
- [x] Blocked route reports metadata to the orchestrator and never mutates Kanban state.
- [x] Focused reporting tests and actual route-context tests pass.
- [x] `make lint` and `make test` pass.

## Non-goals

- Recovery evaluation or reassignment
- Lease/concurrency implementation
- Cron scheduling
- Telegram delivery

## Verification

Canonical commands: `make lint` and `make test`.
