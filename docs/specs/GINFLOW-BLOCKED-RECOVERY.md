# Blocked Kanban Recovery

## Problem Statement

When `ginflow-gate` routing module finds a blocked Kanban card, worker cannot safely resolve the underlying problem. Config errors, persistence failures, unknown failures, and interrupted work need different handling. Without durable blocker metadata and orchestrator ownership, blocked work can be silently abandoned, retried incorrectly, or reassigned multiple times.

## Solution

Worker keeps card `blocked`, appends human-readable and structured blocker evidence, and reports blocker to `gintary`. A fixed-interval cron wakes `gintary`. `gintary` evaluates blocker metadata, reassigns previous worker for recoverable failures, retries unknown failures up to three attempts, and leaves non-recoverable failures blocked. After retry exhaustion, `gintary` reports to human through Telegram. Worker session does not send Telegram.

## User Stories

1. As a worker, I want blocked work to remain blocked, so that I do not falsely claim completion.
2. As a worker, I want to append blocker evidence to the card, so that orchestrator can understand failure without reconstructing session history.
3. As an orchestrator, I want structured blocker metadata, so that recovery decisions are deterministic.
4. As an orchestrator, I want readable card comments, so that humans can inspect recovery history.
5. As an orchestrator, I want to distinguish transient worker failure from `config_error`, so that unsafe retries are avoided.
6. As an orchestrator, I want to distinguish `persist_error`, so that data-integrity failures remain blocked.
7. As an orchestrator, I want unknown blockers retried with a fixed limit, so that ambiguous failures get bounded recovery without infinite loops.
8. As an orchestrator, I want to reassign the previous worker for recoverable work, so that context is preserved.
9. As an orchestrator, I want retry attempts recorded append-only, so that every recovery decision is auditable.
10. As a human, I want exhausted recovery reported through Telegram, so that I can resolve work requiring judgment.
11. As a human, I want non-recoverable cards to remain blocked, so that automation does not hide configuration or persistence problems.
12. As an operator, I want fixed-interval cron execution, so that recovery does not depend on the worker session remaining active.
13. As an operator, I want overlapping cron runs prevented from duplicating actions, so that workers are not reassigned multiple times.
14. As an operator, I want Telegram notifications idempotent, so that one exhausted recovery produces one human alert.
15. As an orchestrator, I want invalid or incomplete metadata to fail closed, so that uncertain state does not mutate Kanban ownership.

## Implementation Decisions

- `ginflow-gate` routing module reports a blocked-card route to orchestrator and does not implement, resolve, or reassign the card.
- Worker appends both a card comment and structured recovery metadata.
- Metadata is append-only. Each blocker and recovery decision is an event; prior evidence is never overwritten.
- Metadata records card ID, workspace, previous assignee, blocker kind, error summary, evidence, attempted commands, timestamp, recovery candidacy, attempt number, maximum attempts, last decision, and decision owner.
- `gintary` owns recovery evaluation, Kanban status/assignee mutation, and Telegram notification decisions.
- A fixed-interval cron wakes `gintary` and scans cards with recovery metadata or pending notification state.
- Recoverable transient failures reassign the previous worker while card remains governed by normal Kanban lifecycle.
- Unknown blockers are retried with maximum three attempts.
- `config_error`, `persist_error`, human-input blockers, and invalid safety state remain blocked without reassignment.
- After three attempts, card remains blocked and `gintary` sends a Telegram report containing card ID, workspace, attempts, blocker events, last error, and required human action.
- Worker session never sends Telegram for this workflow.
- Recovery processing requires an expiring atomic lease identified by orchestrator run ID. Concurrent or locked cards are skipped; expired leases can be retried on a later cron run.
- Recovery events and Telegram notifications use idempotency keys based on card ID and recovery event ID.
- Missing worker, workspace mismatch, terminal card, newer attempt, or retry limit failure blocks mutation and records reason.

## Testing Decisions

- Test highest seam: cron wake-up through `gintary` recovery evaluation to observable Kanban mutation or Telegram decision.
- Use isolated temporary Kanban cards and real CLI/API boundaries where available, not helper-only simulations.
- Assert external behavior: card status, assignee, append-only metadata, comments, retry count, lease behavior, and notification decision.
- Cover recoverable blocker reassignment, unknown blocker retries, three-attempt exhaustion, non-recoverable blockers, invalid metadata, missing previous worker, terminal cards, overlapping runs, expired leases, and duplicate notification prevention.
- Follow existing deterministic Ginflow harness style and project-native `make lint` / `make test` verification.

## Out of Scope

- Automatic resolution of `config_error` or `persist_error`.
- Automatic completion or unblocking of cards.
- Product-scope decisions or human-input resolution.
- Telegram delivery from worker sessions.
- Unlimited retries or adaptive retry limits.
- Deployment or production mutation.

## Further Notes

Telegram delivery failure must keep card blocked and leave pending notification metadata for a later cron run. Recovery policy should fail closed when metadata, workspace, ownership, or persistence state cannot be trusted.

Publication target: project issue tracker with `ready-for-agent` label. Tracker command was not available in current repository context, so this local spec is ready for publication when tracker integration is configured.

Status: contract finalized; tracker publication blocked by missing issue-tracker command/configuration.

The normative append-only event schema, validation and fail-closed rules, recovery boundary, idempotency contract, comment format, and atomicity boundary are finalized in `docs/wayfinding/GINFLOW-BLOCKED-RECOVERY-01.md`. This specification remains consistent with that decision record.
