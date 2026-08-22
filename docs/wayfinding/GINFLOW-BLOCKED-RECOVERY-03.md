# Define recovery lease and idempotency boundary

## Question

Where and how does `gintary` acquire an expiring recovery lease and enforce idempotent reassignment, retry increments, and Telegram decisions across overlapping cron runs?

Type: `wayfinder:grilling`
Status: resolved
Depends on: blocker and recovery metadata contract

Resolution must define lock owner, expiry, stale-lock handling, atomicity, and idempotency key scope.

Tracker publication unavailable; local Markdown ticket placeholder.

---

**Resolution:** resolved

### Decision

`gintary` owns recovery coordination in durable Kanban persistence, not worker process memory. Lease and idempotency state live beside card recovery metadata in the same transactional store. Each lease row is keyed by `card_id`, with `owner_run_id`, `claimed_at`, and `expires_at`; lease duration is 10 minutes. Claim uses one atomic compare-and-set transaction: insert when absent, or replace only when existing `expires_at <= now`; an unexpired lease makes card skipped. The owner renews before expiry while processing. Expired leases are stale and reclaimable; stale owners have no mutation authority.

All card mutation, attempt increment, recovery event append, and lease release commit in one transaction. A failed transaction leaves card, attempt, and lease state unchanged. Reassignment idempotency key is `recovery:<card_id>:<event_id>:<attempt>`; notification key is `telegram:<card_id>:<event_id>`. Each key has a unique constraint. Duplicate retry or notification treats unique-conflict as already applied and performs no second Kanban mutation or Telegram send. Notification row remains `pending` until gateway acknowledgement; delivery failure keeps it pending for a later leased run. Terminal cards and malformed/mismatched metadata are recorded as blocked decisions, not mutated.

This decision resolves storage boundary, expiry, atomic claim, stale-lock handling, duplicate retry prevention, and notification idempotency. Implementation must use a persistent transactional adapter and prove overlapping runs, stale lease reclaim, transaction rollback, and duplicate keys at the end-to-end seam.

**Blocks:** implementation of recovery coordinator

---
