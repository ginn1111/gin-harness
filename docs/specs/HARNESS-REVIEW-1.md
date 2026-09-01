---
status: completed
size: M
scope:
  - Hermes Kanban integration-test harness
owner: ginb
---

# Spec — Native running-to-review transition

## Problem

Current Ginflow lifecycle tests validate `kanban_request_review` gate approval but do not execute Hermes-owned state mutation. They cannot prove a task moves from `running` to `review`.

## Desired behavior

An isolated integration test uses a temporary Hermes Kanban database/runtime to submit a native review request. A valid request changes task status from `running` to `review` and persists review handoff data. A Ginflow-gate rejection does not execute native mutation and leaves status `running`.

## Inputs / outputs

- Input: temporary task in `running`, valid review summary and Ginflow evidence metadata.
- Output: task in `review` with persisted summary and metadata.
- Rejection input: missing or invalid Ginflow evidence.
- Rejection output: task remains `running`.

## Constraints

- Use real Hermes Kanban transition code, not an in-memory status assignment.
- Use temporary isolated state; never mutate live board data.
- Keep Ginflow gate validation and Hermes state mutation assertions distinct.
- Do not modify Hermes core.
- Do not modify existing trace-test edits.
- Canonical verification remains `make test`.

## Acceptance criteria

- [x] Scope and expected transition defined.
- [x] Focused test proves `running` to `review` through native Hermes behavior.
- [x] Valid review summary and metadata persist.
- [x] Rejected review leaves task `running`.
- [x] `make lint` and `make test` pass.

## Edge cases

- Missing Ginflow evidence blocks before state mutation.
- Test must fail clearly when native Hermes review API is unavailable or changes contract.
