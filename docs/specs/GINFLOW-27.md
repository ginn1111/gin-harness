---
status: in_progress
size: S
scope:
  - plugins/ginflow-gate/ pre_tool_call guard for kanban_block and test
owner: ginb
---

# GINFLOW-27 — kanban_block guard

Refs: ginn1111/gin-harness#26 (parent spec), #28 (this slice). Shared contract: `docs/specs/GINFLOW-26.md` (B1 to B8) and issue #26.

## Objective

With trace on, `ginflow-gate` guards `kanban_block` so the worker supplies a reliable kind and an actionable reason.

## Contract

- With trace on, a missing or unknown `kind` **must** be rejected and the message **must** name the valid kinds.
- `needs_input` and `capability` **must** be rejected unless `reason` has a `required_action:` line.
- `transient` **must** pass with a short reason. `dependency` **must** pass untouched.
- With trace off the guard **must not** act.

## Acceptance criteria

- [ ] Missing kind rejected, message names valid kinds
- [ ] Invalid kind rejected
- [ ] `needs_input` / `capability` without `required_action` rejected
- [ ] `transient` with short reason passes
- [ ] Trace off: guard inactive
- [ ] `make lint && make test` pass
