---
status: approved
size: XL
scope: GINFLOW-V2-10
owner: ginb
---

# Plan — Prove version 1 compatibility and version 2 lifecycle

## Objective

Demonstrate the complete artifact-first lifecycle through the highest existing integration seam while proving that already-active legacy cards still follow version 1 rules. Make documentation, validator, plugin guidance, gates, review, drift handling, and lifecycle behavior pass together.

## Dependencies

08 — Reshape, cancel, and rebaseline active packages; 09 — Migrate related documentation.

## Execution

- Implement the smallest complete vertical slice described by this plan.
- Preserve version 1 behavior until the explicit contraction unit.
- Run project-native verification and record exact evidence on the Kanban card.

## Acceptance criteria

- [ ] The end-to-end lifecycle test covers Shaping output, blocked cards, validation, frontier release, dependencies, goal-mode work, exceptions, review, integration, drift, and completion.
- [ ] Active version 1 cards retain their existing lifecycle behavior.
- [ ] Focused tests cover validator and exception failures that are impractical to assert through the lifecycle seam.
- [ ] Canonical repository lint and full deterministic tests pass.
