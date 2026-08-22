# Define cron-to-gintary wake-up contract

## Question

What fixed-interval cron schedule and wake-up interface should invoke `gintary`, and how should it select blocked cards without scanning or mutating unrelated work?

Type: `wayfinder:grilling`
Status: resolved
Depends on: blocker and recovery metadata contract

## Resolution

Recovery policy is fixed:

- Retryable blockers: transient worker failures and unknown blocker kinds. Reassign to `previous_assignee`, preserving card `blocked` state until normal Kanban transition.
- Non-retryable blockers: `config_error`, `persist_error`, `human_input`, malformed or incomplete safety metadata, workspace mismatch, missing previous worker, and terminal cards (`done`, `cancelled`, `archived`). Leave card blocked and record reason; never mutate ownership.
- Unknown blockers: retry at most three attempts. Attempts are append-only and counted per blocker event. After attempt three, leave card blocked and emit one idempotent Telegram report for human action.
- Missing worker or workspace mismatch: fail closed; do not reassign. Record reason for operator review.
- Terminal card: skip mutation and record `terminal_card`; do not notify as retry exhaustion.
- Concurrent recovery: require an expiring atomic lease keyed by orchestrator run ID. Locked cards are skipped; expired leases are eligible on later wake-up.
- Duplicate processing: use `card_id:event_id` idempotency keys for recovery decisions and `telegram:card_id:event_id` for notifications.
- Worker sessions never send Telegram. `gintary` owns evaluation, reassignment, and notification decisions.

Cron/wake-up integration must select only cards carrying recovery metadata or pending notification state, and must fail closed when selection scope, workspace, or metadata cannot be trusted.

**Decision:** approved for implementation. No implementation is part of this decision card.

### Cron wake-up contract

- Host-owned cron runs every 5 minutes (`*/5 * * * *`). No worker profile schedules recovery.
- Cron invokes `gintary` through its profile CLI with one-shot input: `--job blocked-recovery --run-id <unique-run-id>`. `gintary` owns all decisions and Kanban mutations; cron records output and exit code only.
- Select only cards in `blocked` state with unhandled append-only recovery events or `pending` notification rows. Order oldest event timestamp, then card ID. Apply lease rules from ticket 03 before processing.
- Scope is one configured Kanban board, target workspace, and `gintary` profile. Ignore unrelated boards/workspaces, terminal cards, and cards without explicit markers.
- If `gintary` is unavailable, leave cards and notifications unchanged, retry next tick, and raise one host-monitoring alert after three consecutive failed ticks. Clear failure streak after successful run. Never reassign cards or send Telegram from worker sessions.

---

**Resolution:** resolved

**Blocks:** implementation of cron wake-up and recovery coordinator

---

Tracker publication unavailable; local Markdown ticket placeholder.
