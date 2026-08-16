---
status: completed
size: XS
scope: blocker metadata decision validation
owner: ginb
---

# Brief — GINFLOW-13 Validate blocker metadata contract

## Objective

Validate, finalize, and commit the append-only blocker and recovery metadata decision before implementation cards proceed.

## Scope

- `docs/wayfinding/GINFLOW-BLOCKED-RECOVERY-01.md`
- Consistency with `docs/specs/GINFLOW-BLOCKED-RECOVERY.md`
- Decision evidence and completion baseline only

## Acceptance criteria

- [x] Event schema and required fields are explicit.
- [x] Recoverable and non-recoverable blocker kinds are fixed.
- [x] Malformed metadata fails closed without reassignment or notification.
- [x] Unknown failures use a maximum of three attempts.
- [x] Recovery decisions and notifications have idempotency keys.
- [x] Lease, re-read, validation, event append, and ownership/status mutation boundaries are explicit.
- [x] Human-readable comment format excludes secrets and raw PII.
- [x] Contract is consistent with the blocked-recovery specification.
- [x] Linked decision artifact is committed.
- [x] `make lint` passes.

## Non-goals

- Runtime recovery implementation
- Kanban schema migration
- Telegram delivery implementation

## Verification

`make lint` passed. The linked decision is committed at `1e083e796175eafc4e021f55d693a56c1759b442`.
