# Define Telegram escalation contract

## Question

What Telegram gateway and delivery contract should `gintary` use after retry exhaustion, and how should delivery failure remain pending without changing card safety state?

Type: `wayfinder:grilling`
Status: completed
Depends on: blocker and recovery metadata contract

Resolution must define recipient, message contents, delivery idempotency, retry policy, and missing-gateway behavior.

Tracker publication unavailable; local Markdown ticket placeholder.

---

**Resolution:** resolved

## Decision

- **Owner:** `gintary`, never the worker session, decides and sends recovery escalation.
- **Recipient:** one configured human-operator Telegram destination from the gateway configuration. The destination must be gateway-connected; local/TUI `origin` delivery is not valid. Missing or invalid destination configuration is a fail-closed `config_error`: keep the card blocked and make no delivery attempt.
- **Trigger:** create one notification for an exhausted recovery event when `attempt == max_attempts == 3`. The notification idempotency key is `telegram:<card_id>:<blocker_event_id>`.
- **Message:** bounded plain text containing card ID, canonical workspace, blocker kind, attempts/max, safe last-error summary, and required human action. Exclude secrets, tokens, credentials, raw logs, and raw PII.
- **Append-only state:** append `pending` before delivery. On success append `sent` with gateway receipt and RFC3339 UTC timestamp. On failure append a new `pending` retry event with safe failure summary, delivery-attempt count, and next eligible time. Never overwrite earlier events.
- **Retry:** fixed-interval recovery cron retries only eligible `pending` notifications, with bounded exponential delay and at most three delivery attempts. Overlapping runs use the same idempotency key and lease so only one send is in flight.
- **Exhaustion:** after three delivery failures append `failed`, keep the card blocked, record an operator-repair comment, and retain the notification for manual replay after gateway repair. Never unblock, complete, or silently discard the alert.
- **Gateway uncertainty:** a timeout or missing receipt is not success. Preserve `pending`, release/expire the lease safely, and let a later cron re-evaluate idempotently.

This contract is consistent with `docs/specs/GINFLOW-BLOCKED-RECOVERY.md` and the append-only event contract in `docs/wayfinding/GINFLOW-BLOCKED-RECOVERY-01.md`.

**Blocks:** Telegram recovery implementation and exhausted-recovery integration tests

---

## Decision ticket

This is a decision ticket, not an execution task. Resolve one decision per session.
