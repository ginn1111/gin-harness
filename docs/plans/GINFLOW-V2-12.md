---
status: approved
size: XL
scope: GINFLOW-V2-12
owner: ginb
---

# Plan — Contract legacy routing

## Objective

Complete the expand–migrate–contract sequence after every active version 1 card closes. Remove Work Size, Direct Work, conditional artifact routing, temporary compatibility branches, and obsolete tests so version 2 becomes the sole Ginflow workflow.

## Dependencies

11 — Pilot version 2 and enable it for new initiatives; closure of all active version 1 cards.

## Execution

- Implement the smallest complete vertical slice described by this plan.
- Preserve version 1 behavior until the explicit contraction unit.
- Run project-native verification and record exact evidence on the Kanban card.

## Acceptance criteria

- [ ] No active version 1 card remains before contraction begins.
- [ ] Work Size, Direct Work, conditional artifact routing, and temporary compatibility code are removed.
- [ ] Obsolete legacy tests and documentation are deleted or replaced by version 2 assertions.
- [ ] Canonical repository lint and full deterministic tests pass with version 2 as the sole workflow.
