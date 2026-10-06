---
status: approved
size: XL
scope: GINFLOW-V2-05
owner: ginb
---

# Plan — Run workers continuously until done or exception

## Objective

Dispatch each runnable implementation card in goal mode with a bounded turn budget and enough authority to finish normal engineering work. Workers continue through implementation choices, compile failures, worker-caused test failures, and Plan-step refinements, stopping only for a defined Worker Exception or successful review handoff.

## Dependencies

04 — Validate package and release runnable frontier.

## Execution

- Implement the smallest complete vertical slice described by this plan.
- Preserve version 1 behavior until the explicit contraction unit.
- Run project-native verification and record exact evidence on the Kanban card.

## Acceptance criteria

- [ ] Runnable cards dispatch with goal mode and approved turn budgets of 20, 40, or at most 60 turns.
- [ ] Workers can inspect, edit card-scoped code, add tests, retry verification, and revise non-contractual Plan steps without interruption.
- [ ] Ordinary implementation failures do not become Worker Exceptions.
- [ ] Contract, scope, acceptance, dependency, security-boundary, and verification changes cannot proceed silently.
