# Wayfinder Map — Blocked Kanban Recovery

## Destination

A handoff-ready spec and decision map for safe blocked-card recovery: worker evidence, interval cron wake-up, `gintary` decision, bounded reassignment, fail-closed blockers, and Telegram escalation.

## Notes

Domain: Ginflow routing, Hermes Kanban, orchestrator recovery.
Consult: `ginflow-gate` routing module, `grilling`, `domain-modeling`, verification-before-completion.
Planning only. No implementation in this map.

## Decisions so far

- [Blocked Kanban Recovery spec](../specs/GINFLOW-BLOCKED-RECOVERY.md) — worker reports; `gintary` owns recovery and escalation.
- [Define blocker and recovery metadata contract](GINFLOW-BLOCKED-RECOVERY-01.md) — append-only events, fail-closed validation, guarded atomic mutation.
- [Define cron-to-gintary wake-up contract](GINFLOW-BLOCKED-RECOVERY-02.md) — host cron every five minutes; scoped `gintary` one-shot run.
- [Define recovery lease and idempotency boundary](GINFLOW-BLOCKED-RECOVERY-03.md) — ten-minute durable per-card lease; transactional compare-and-set and unique keys.
- [Define Telegram escalation contract](GINFLOW-BLOCKED-RECOVERY-04.md) — orchestrator-owned bounded escalation with pending retry state.
- [Define real-agent integration test seam](GINFLOW-BLOCKED-RECOVERY-05.md) — subprocess seam with temporary DB/workspace and recording gateway.
- [Define real-agent recovery test seam](GINFLOW-BLOCKED-RECOVERY-06.md) — end-to-end observable assertions and canonical verification.

## Not yet specified

- No remaining decision tickets identified for this destination.
- Implementation decomposition, target ownership, and card-level acceptance remain implementation planning, not wayfinder decisions.

## Out of scope

- Automatic resolution of `config_error` or `persist_error`.
- Automatic card completion or unblocking.
- Product-scope decisions.
- Production deployment.

## Child tickets

- [Define blocker and recovery metadata contract](GINFLOW-BLOCKED-RECOVERY-01.md) — `wayfinder:grilling`
- [Define cron-to-gintary wake-up contract](GINFLOW-BLOCKED-RECOVERY-02.md) — `wayfinder:grilling`
- [Define recovery lease and idempotency boundary](GINFLOW-BLOCKED-RECOVERY-03.md) — `wayfinder:grilling`
- [Define Telegram escalation contract](GINFLOW-BLOCKED-RECOVERY-04.md) — `wayfinder:grilling`
- [Define real-agent integration test seam](GINFLOW-BLOCKED-RECOVERY-05.md) — `wayfinder:grilling`

Blocking order: ticket 01 first; tickets 02–05 depend on metadata contract. Ticket 03 also depends on Kanban mutation semantics discovered in 01.

Status: wayfinder clear for implementation; all six decision tickets resolved.

Tracker publication remains unavailable because no external issue-tracker integration is configured. These local Markdown files are canonical until tracker integration exists.
