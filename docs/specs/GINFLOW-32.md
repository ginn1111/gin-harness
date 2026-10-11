---
status: in_progress
scope:
  - skills/ginflow/references/trace-routing.md
  - skills/ginflow/SKILL.md pointer line
owner: ginb
---

# GINFLOW-32 — Agent reference and skill pointer

Refs: ginn1111/gin-harness#26 (parent spec), #33 (this slice). Shared contract: `docs/specs/GINFLOW-26.md` (B1 to B8) and issue #26.

## Objective

Workers and the repair profile have one reference for block-kind routing.

## Contract

- The reference **must** cover block kinds and when to use each (`capability` only when a human must act), the `required_action` contract, critical and repairable hook behavior, the injected repair context, and the credential constraint (`ginb` has Slack only).
- One pointer line **must** be added to the `ginflow` skill entry. No new skill.
- The reference **must** match shipped behavior of GINFLOW-27, 28, 30 and 31.

## Acceptance criteria

- [ ] Reference documents kinds, `required_action`, both routes, injected context, credential constraint
- [ ] One pointer line added to the `ginflow` skill entry
- [ ] Reference matches shipped behavior
- [ ] `make lint && make test` pass
