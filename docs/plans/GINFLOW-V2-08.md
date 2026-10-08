---
status: approved
size: XL
scope: GINFLOW-V2-08
owner: ginb
---

# Plan — Reshape, cancel, and rebaseline active packages

## Objective

Handle material discoveries and cancellation without corrupting active execution. Affected branches pause and return to Shaping for artifact revision, approval, a new committed baseline, and validation; independent branches continue. Unit and initiative cancellation preserve truthful dependencies and global acceptance.

## Dependencies

06 — Recover workers without unnecessary human interruption; 07 — Review, rework, and integrate completed units.

## Execution

- Implement the smallest complete vertical slice described by this plan.
- Preserve version 1 behavior until the explicit contraction unit.
- Run project-native verification and record exact evidence on the Kanban card.

## Acceptance criteria

- [ ] Material Contract, Spec, scope, acceptance, dependency, or verification changes pause only affected branches and require reapproval.
- [ ] A new baseline and successful package validation are required before affected work resumes.
- [ ] Independent unaffected branches can continue.
- [ ] Unit and initiative cancellation archive the correct cards and cannot silently weaken global acceptance.
