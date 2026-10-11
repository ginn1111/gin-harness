---
status: in_progress
scope:
  - plugins/ginflow-gate/ block routing fallback chain and test
owner: ginb
---

# GINFLOW-28 — Critical delivery fallbacks

Refs: ginn1111/gin-harness#26 (parent spec), #29 (this slice). Shared contract: `docs/specs/GINFLOW-26.md` (B1 to B8) and issue #26.

## Objective

A critical block is never lost silently: when no target is set it uses native notify subscriptions, and when no destination exists or the push fails a card comment carries the notice.

## Contract

- With no `ginflow.notify.target`, the push **must** use the task's native notify subscriptions.
- With no destination, or on push failure, the notice **must** be written as a card comment and the task **must** stay `blocked`.
- A hook failure **must not** break the block transition.

## Acceptance criteria

- [ ] No target: native subscription destination used
- [ ] No destination: card comment carries the notice; task `blocked`
- [ ] Push failure: card comment carries the notice; task `blocked`
- [ ] Hook failure never breaks the block transition
- [ ] `make lint && make test` pass
