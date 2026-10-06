---
status: approved
size: XL
scope: GINFLOW-V2-04
owner: ginb
---

# Plan — Validate package and release runnable frontier

## Objective

Validate the complete approved package and release only its safely runnable frontier. Invalid artifacts, dependency graphs, links, ownership, workspace allocation, commits, or baseline evidence fail before dispatch; valid independent root cards unblock while descendants remain gated.

## Dependencies

03 — Create blocked cards from approved Work Units.

## Execution

- Implement the smallest complete vertical slice described by this plan.
- Preserve version 1 behavior until the explicit contraction unit.
- Run project-native verification and record exact evidence on the Kanban card.

## Acceptance criteria

- [ ] Validation rejects missing or unapproved artifacts, incomplete required fields, duplicate keys, broken links, cycles, dirty paths, and missing baseline evidence.
- [ ] Validation rejects simultaneously runnable cards that share a mutable workspace without isolation.
- [ ] Successful validation unblocks only independent root cards.
- [ ] Child cards remain gated until all parent cards are done.
