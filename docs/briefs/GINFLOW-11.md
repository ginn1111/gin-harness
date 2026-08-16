# GINFLOW-11 — Empty-board work-mode and work-size decision matrix

**Status: proposed**

## Objective

Make empty-board work-mode, scope-size, and artifact decisions explicit in the `Gin-harness-flow` diagram page.

## Scope

- Add root-cause and requirement-clarity decisions.
- Add XS/S, M, and L/XL/risky scope-size branches.
- Show brief/spec/plan artifact mapping.
- Show split-card guidance for large or risky work.
- Preserve existing diagram pages, style, and content.

## Acceptance criteria

- Unknown root cause routes to Investigation.
- Known cause with unclear requirements routes to Brainstorming/clarification.
- Clear requirements route through XS/S, M, and L/XL/risky decisions.
- Diagram shows artifact mapping and card-splitting guidance.
- `Gin-harness-flow` remains readable and opens in draw.io.
- Existing diagram content remains intact.
- `make lint && make test` passes.

## Verification

- Validate diagram XML structure and page/cell references.
- Open the `.drawio` file in draw.io desktop when available.
- Run `make lint && make test`.
- Review diff for diagram-only scope plus linked brief.

## Out of scope

- Implementing the decision matrix in Ginflow runtime code.
- Changing Kanban policy or profile configuration.
- Modifying `Harness system overview` page.

## Test seam

Use diagram XML validation plus existing setup-repo verification. Confirm the target page contains explicit decision labels and connected branches; preserve the second page byte-for-byte where practical.

**Status: completed**
