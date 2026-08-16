# Define blocker and recovery metadata contract

## Question

What exact append-only blocker and recovery event schema should worker and `gintary` use, and which Kanban operations must be atomic before reassignment is allowed?

Type: `wayfinder:grilling`
Status: completed
Depends on: none
Blocks: cron contract, lease/idempotency boundary, Telegram contract, integration-test seam

Resolution must define blocker kinds, required fields, recovery candidate rules, attempt counting, malformed metadata behavior, and observable card comment format.

Tracker publication unavailable; local Markdown ticket placeholder.

---

**Resolution:** resolved

## Decision

Use append-only recovery events as the sole machine-readable contract. Each event is one JSON object in `blocker_events`, never edited or deleted:

```json
{
  "event_id": "<unique stable ID>",
  "event_type": "blocked|recovery_decision|notification",
  "card_id": "<Kanban card ID>",
  "workspace": "<canonical absolute workspace path>",
  "previous_assignee": "<profile>",
  "blocker_kind": "transient|unknown|config_error|persist_error|human_input",
  "error_summary": "<safe single-line summary>",
  "evidence": ["<safe strings>"],
  "attempted_commands": ["<safe commands>"],
  "occurred_at": "<RFC3339 UTC timestamp>",
  "attempt": 0,
  "max_attempts": 3,
  "recovery_candidate": true,
  "decision": "pending|reassign|stay_blocked|notify_human|skip",
  "decision_owner": "worker|gintary|system",
  "idempotency_key": "<card_id>:<event_id>"
}
```

Required fields: `event_id`, `event_type`, `card_id`, `workspace`, `previous_assignee`, `blocker_kind`, `error_summary`, `occurred_at`, `attempt`, `max_attempts`, `decision`, and `decision_owner`. `evidence`, `attempted_commands`, and `recovery_candidate` are required on `blocked` events. Recovery-decision and notification events additionally require `idempotency_key`. Values must be type-valid, non-empty where scalar, `attempt` must be integer `>= 0`, and `max_attempts` must equal `3` for automated recovery.

`transient` is recoverable; `unknown` is recoverable until attempt `3`. `config_error`, `persist_error`, and `human_input` are non-recoverable. Recovery candidate must be false for non-recoverable kinds. Reassignment is allowed only when metadata validates, card is non-terminal, workspace equals canonical current workspace, previous worker exists, and event has not been processed. `gintary` owns status/assignee mutation and notification. Lease acquisition, event append, and mutation use event idempotency; concurrent or expired leases skip safely. Malformed or incomplete metadata fails closed: append a `recovery_decision` with `decision=stay_blocked`, `decision_owner=system`, reason `malformed_safety_state`; do not reassign, unblock, complete, or notify.

Kanban comment format (one append-only comment per event):

`[ginflow-recovery] event=<event_id> type=<event_type> kind=<blocker_kind> attempt=<attempt>/<max_attempts> decision=<decision> owner=<decision_owner> reason=<safe single-line reason>`

Comments contain no secrets or raw PII. Retry exhaustion leaves card blocked and emits one notification event keyed `telegram:<card_id>:<event_id>`; delivery failure leaves notification pending for next cron scan.

## Atomicity boundary

Before reassignment, `gintary` must acquire an expiring lease, re-read the card and newest event, and verify idempotency, workspace, ownership, and non-terminal state. It must then append the decision event and mutate assignee/status in one guarded Kanban transaction. If transaction support is unavailable, fail closed and leave the card blocked; no partial decision append or reassignment is accepted.

**Decision recorded:** blocker kinds, schema, validation/fail-closed behavior, recovery rules, attempt limit, idempotency contract, comment format, and atomic mutation boundary are fixed above and consistent with `docs/specs/GINFLOW-BLOCKED-RECOVERY.md`.
