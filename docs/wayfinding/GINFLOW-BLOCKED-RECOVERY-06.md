# Define real-agent recovery test seam

## Decision

Use one isolated subprocess-level integration seam rooted at a temporary Kanban DB and temporary workspace. Start the real `gintary` recovery entrypoint through its supported CLI/API boundary; inject only infrastructure adapters at process edges: deterministic clock, fake cron trigger, and recording Telegram gateway. Do not call recovery helpers directly.

The test owns full lifecycle:

1. Seed temporary card in `blocked` with append-only blocker event and previous worker identity.
2. Trigger one interval wake-up through cron boundary.
3. Let real `gintary` parse metadata and evaluate recovery.
4. Observe Kanban persistence and Telegram recorder through external boundaries.
5. Repeat wake-ups with same event ID to prove lease/idempotency behavior.

## Fixture boundary

- Temporary Kanban DB, created per test and deleted after run.
- Temporary workspace path matching card workspace exactly.
- Fixed worker/profile registry containing previous worker and one invalid/missing-worker case.
- Fake clock controlled by test; no wall-clock sleeps.
- Cron trigger adapter that invokes the real orchestrator command once per tick.
- Recording Telegram gateway; no network and no worker-session Telegram calls.
- Real CLI/API serialization, validation, lease, mutation, and notification code.

Fixtures must not mock Kanban repository methods, recovery evaluator, or orchestrator decision logic. Those are the seam under test.

## Observable assertions

Assert only durable or boundary-visible behavior:

- card stays `blocked` for every recovery path;
- recoverable transient blocker reassigns previous worker exactly once;
- unknown blocker increments append-only attempt events, then stops at three attempts;
- `config_error`, `persist_error`, invalid metadata, missing worker, workspace mismatch, and terminal card cause no reassignment;
- comments and structured metadata remain append-only and include decision owner/reason;
- active lease prevents overlapping wake-ups; expired lease permits later processing;
- exhausted recovery produces exactly one Telegram recorder event keyed by card ID plus recovery event ID;
- Telegram failure leaves card blocked with pending notification metadata;
- duplicate cron ticks do not duplicate reassignment or notification.

## Telegram boundary

Integration tests assert gateway invocation and idempotency key, not Telegram service delivery. Gateway contract test separately verifies payload shape and retry classification. No credentials, network, or real Telegram chat belongs in canonical test suite.

## Canonical verification

From target repository, run:

    make lint && make test

The integration suite must run deterministically in isolated temporary resources and fail if it falls back to helper-only calls. Ginflow harness validation remains required for workflow changes.

## Scope guard

This decision defines test seam and acceptance observables only. It does not implement recovery runtime, cron, Kanban persistence, or Telegram gateway.

Status: resolved
Date: 2026-08-15

---

Source decision ticket: [GINFLOW-BLOCKED-RECOVERY-05](GINFLOW-BLOCKED-RECOVERY-05.md)
Target spec: [GINFLOW-BLOCKED-RECOVERY](../specs/GINFLOW-BLOCKED-RECOVERY.md)
