---
status: in_progress
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

- [ ] Second `transient` block pushes a critical notice
- [ ] Task stays `blocked`; not reassigned to `gintary` again
- [ ] First `transient` block still auto-repairs
- [ ] `make lint && make test` pass

## TBD

- How a prior auto-repair is detected (card comment marker vs event history) — owner: ginb. Must use card data only; no new persistence (see #26).
