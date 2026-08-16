# Define real-agent integration test seam

## Question

What single highest test seam proves blocked-card recovery across worker evidence, interval cron wake-up, `gintary` evaluation, Kanban reassignment, retry exhaustion, and Telegram escalation using isolated real-agent integration fixtures?

Type: `wayfinder:grilling`
Status: completed
Depends on: blocker and recovery metadata contract

Resolution defines fixture boundary, observable outputs, failure cases, and verification command.

Tracker publication unavailable; local Markdown ticket placeholder.

---

**Resolution:** decided — Telegram escalation is orchestrator-owned and targets configured human operator chat (`TELEGRAM_CHAT_ID` / gateway equivalent), never worker or arbitrary card assignee. One alert per exhausted recovery event, keyed by `telegram:<card_id>:<event_id>`.

**Contract:**

- **Recipient:** configured human operator destination from gateway configuration. Missing recipient configuration is a fail-closed `config_error`; card stays `blocked`, no delivery attempt is made.
- **Message:** plain-text, bounded, actionable summary containing card ID, workspace, blocker kind, attempt count/max (`3/3`), last error, and required human action. Do not include secrets, tokens, or full raw logs.
- **Pending state:** before delivery, append notification metadata with idempotency key, payload summary, status `pending`, attempt count, and timestamps. On success mark `sent` with delivery receipt/time. Preserve all transitions append-only.
- **Retry policy:** fixed-interval cron retries `pending` notifications with bounded exponential delay, maximum three delivery attempts per cron-visible notification event. Idempotency key prevents duplicate alerts across overlapping runs or timeouts.
- **Gateway failure:** keep card `blocked`; retain/update `pending` notification metadata with failure summary and next retry time. After delivery retry exhaustion, retain `pending`/`failed` state and surface gateway failure for human/operator repair; never unblock, complete, or silently discard alert.
- **Ownership:** `gintary` owns recipient selection, formatting, state transition, retry, and escalation decision. Worker sessions never send Telegram.

**Blocks:** none

---

## Decision ticket

This is a decision ticket, not an execution task. Resolve one decision per session.
