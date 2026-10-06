---
status: approved
size: XL
scope: GINFLOW-V2-01
owner: ginb
---

# Plan — Define version 2 Execution Package contract

## Objective

Establish the version 2 domain contract so Ginflow can recognize and validate a minimal artifact-first Execution Package without changing active version 1 behavior. Define canonical vocabulary, artifact lifecycles, stable keys, approval evidence, package baseline rules, and the architectural decision behind the migration.

## Dependencies

None — can start immediately.

## Execution

- Implement the smallest complete vertical slice described by this plan.
- Preserve version 1 behavior until the explicit contraction unit.
- Run project-native verification and record exact evidence on the Kanban card.

## Acceptance criteria

- [ ] Canonical terms and lifecycle states are documented and used consistently.
- [ ] An ADR records the artifact-first decision and its trade-offs.
- [ ] A minimal approved version 2 package validates through one deterministic seam.
- [ ] Existing version 1 behavior remains unchanged.
