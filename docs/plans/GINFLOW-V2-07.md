---
status: approved
size: XL
scope: GINFLOW-V2-07
owner: ginb
---

# Plan — Review, rework, and integrate completed units

## Objective

Preserve evidence-backed review while keeping rework autonomous. Reviewers either complete valid units or return exact evidence and a next action; returned workers resume their goal loop. After every required branch completes, the Integration Card owns cross-unit fixes, global acceptance, and initiative-level verification.

## Dependencies

05 — Run workers continuously until done or exception.

## Execution

- Implement the smallest complete vertical slice described by this plan.
- Preserve version 1 behavior until the explicit contraction unit.
- Run project-native verification and record exact evidence on the Kanban card.

## Acceptance criteria

- [ ] Reviewers approve or request changes without editing worker implementation.
- [ ] Returned workers resume the same card and goal loop without routine user interruption.
- [ ] The Integration Card starts only after all required parent cards are done.
- [ ] Initiative-level verification and cross-unit acceptance are recorded as completion evidence.
