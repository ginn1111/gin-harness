---
status: completed
size: XL
scope: GINFLOW-V2-02
owner: ginb
---

# Plan — Shape and approve complete execution packages

## Objective

Let Gin and the interactive agent brainstorm, gather feedback, inspect the repository read-only, and produce a complete Work Contract, Spec, Work Unit split, dependency graph, verification strategy, and Plan per unit before implementation starts. One explicit approval covers the entire package.

## Dependencies

01 — Define version 2 Execution Package contract.

## Execution

- Implement the smallest complete vertical slice described by this plan.
- Preserve version 1 behavior until the explicit contraction unit.
- Run project-native verification and record exact evidence on the Kanban card.

## Acceptance criteria

- [ ] Shaping produces every required artifact without product-code mutation or worker dispatch.
- [ ] One approval records approver identity and RFC3339 UTC time.
- [ ] Materially incomplete packages cannot become approved.
- [ ] Stable initiative and unit keys exist before Hermes task IDs.
