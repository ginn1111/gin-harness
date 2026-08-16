---
status: completed
size: XS
scope: Telegram recovery escalation decision
owner: ginb
---

# Brief — GINFLOW-15 Validate Telegram escalation contract

## Objective

Finalize the orchestrator-owned Telegram escalation contract used after blocked-card recovery exhaustion.

## Scope

- `docs/wayfinding/GINFLOW-BLOCKED-RECOVERY-04.md`
- Consistency with the blocked-recovery spec and append-only event contract
- Decision evidence only; no gateway or runtime implementation

## Acceptance criteria

- [x] Recipient is one configured, gateway-connected human-operator Telegram destination.
- [x] Missing recipient configuration fails closed without a delivery attempt.
- [x] Trigger and idempotency key are deterministic per exhausted recovery event.
- [x] Message contents are bounded, actionable, and exclude secrets, raw logs, and raw PII.
- [x] Notification state transitions are append-only.
- [x] Delivery retries are bounded to three attempts with deterministic eligibility.
- [x] Gateway timeout or missing receipt is not treated as success.
- [x] Delivery exhaustion keeps the card blocked and retains manual replay state.
- [x] Worker sessions never send Telegram for this workflow.
- [x] `make lint` passes.

## Non-goals

- Telegram gateway configuration
- Runtime notification implementation
- Production delivery

## Verification

Canonical command: `make lint`.
