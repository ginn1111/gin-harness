---
status: completed
size: M
scope: kanban-review-lifecycle
owner: gintary
---

# Kanban Review Lifecycle Design

## Objective

Define one review lifecycle for governed Ginflow work while preserving component boundaries:

- Hermes Kanban owns card states, claims, assignments, and review transitions.
- Ginflow skill guides worker and reviewer behavior.
- `ginflow-gate` validates Ginflow-specific evidence at review and completion boundaries.
- Ginflow must not duplicate Hermes lifecycle state machinery.

## Lifecycle

1. Worker claims a ready card and performs scoped work.
2. Worker runs canonical verification, finalizes linked artifacts, and prepares verification evidence.
3. Worker calls native `kanban_request_review` with summary and metadata.
4. `ginflow-gate` validates required card fields, verification evidence, commit alignment, linked artifacts, and drift. Invalid evidence leaves card with worker. Valid evidence allows transition to `review`.
5. Reviewer profile claims card from `review` and independently checks scope, acceptance, diff, tests, linked artifacts, evidence, and relevant workspace warnings.
6. Valid review: reviewer calls native `kanban_complete`. `ginflow-gate` repeats authoritative evidence validation before Hermes marks card `done`.
7. Invalid review: reviewer investigates enough to produce an actionable handoff, then calls native `kanban_request_changes`. Hermes returns card to original worker under normal dependency gating.
8. Worker fixes issue, reruns verification, refreshes evidence, and requests review again.

`kanban_block` remains reserved for external blockers. Review findings use `kanban_request_changes` and do not count as blocker-loop failures.

## Rejection Handoff

Keep rejection metadata minimal:

```yaml
reason: <what failed>
evidence: <file:line, failing command, or gate error>
next_action: <specific worker fix>
```

`kanban_request_changes.reason` carries concise summary. Review-run metadata carries durable repair context.

## Ownership

| Component | Responsibility |
| --- | --- |
| Hermes Kanban | State transitions, claims, reviewer dispatch, reassignment to original worker, dependency gating, review-run persistence |
| Worker profile | Implementation, canonical verification, artifact finalization, review request, rework |
| Reviewer profile | Independent validation, defect investigation, completion or actionable return |
| Ginflow skill | Agent guidelines and evidence expectations |
| `ginflow-gate` | Validation at `kanban_request_review` and `kanban_complete`; no lifecycle mutation |

## Validation Boundaries

Both transitions validate the same core evidence:

- complete card shape;
- canonical verification result;
- verification commit and artifact-baseline commit alignment;
- exact linked artifact paths;
- completed linked artifact lifecycle state;
- no linked-artifact drift.

Final completion revalidates evidence because repository state may change during review.

## Error Handling

- Missing or stale worker evidence: reject `kanban_request_review`; worker repairs evidence.
- Reviewer finds implementation defect: investigate, record minimal handoff, call `kanban_request_changes`.
- Final gate rejects completion: reviewer investigates gate result, records handoff, returns card to worker.
- External dependency blocks review: use `kanban_block` with actionable context.

## Test Contract

Coverage must prove:

1. Valid review request enters review.
2. Invalid evidence prevents review transition.
3. Valid reviewer completion reaches done.
4. Final drift prevents completion.
5. Rejection requires `reason`, `evidence`, and `next_action`.
6. Rejection restores original worker assignment and respects parent gating.
7. Rework can repeat review cycle without blocker-loop escalation.
8. Direct Work behavior remains unchanged.
9. Canonical diagram, Markdown architecture, skill guidance, plugin behavior, and tests agree.

Repository verification: `make lint` followed by `make test`.
