---
status: completed
scope:
  - plugins/ginflow-gate/ block routing repeat guard and test
owner: ginb
---

# GINFLOW-31 — Repeat-block escalation

Refs: ginn1111/gin-harness#26 (parent spec), #32 (this slice). Shared contract: `docs/specs/GINFLOW-26.md` (B1 to B8) and issue #26.

## Objective

One auto-repair per task. A second repairable block on the same task becomes critical, so worker and `gintary` cannot ping-pong.

## Contract

- A second `transient` block on the same task **must** be treated as critical and pushed through the full fallback chain.
- The task **must** stay `blocked` and **must not** be reassigned to `gintary` again.
- The first `transient` block **must** still auto-repair.

## Acceptance criteria

- [x] Second `transient` block pushes a critical notice
- [x] Task stays `blocked`; not reassigned to `gintary` again
- [x] First `transient` block still auto-repairs
- [x] `make lint && make test` pass

## TBD

- Resolved: prior auto-repair detected by existing `[ginflow] origin=worker` card comment (card data only, no new persistence).
