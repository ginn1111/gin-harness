---
status: ready
size: S
scope: ginflow-gate completion lifecycle
owner: ginb
---

# Brief — GINFLOW-8 Complete linked documents before Kanban completion

## Objective

Update `ginflow-gate` so an attempted `kanban_complete` gives the agent deterministic context to mark all linked target-local briefs, specs, and plans completed before retrying card completion.

## Scope

- `plugins/ginflow-gate/gate.py`
- `plugins/ginflow-gate/routing.py` only if pre-LLM context is required
- `plugins/ginflow-gate/test_ginflow_gate.py`
- `skills/ginflow/SKILL.md` completion guidance
- This brief

## Acceptance criteria

- [ ] A `kanban_complete` attempt detects linked target-local documents not marked completed.
- [ ] The agent receives deterministic guidance listing documents that must be finalized before retrying.
- [ ] Completion fails closed while linked documents remain active.
- [ ] External links and unrelated files are not mutated or treated as local completion documents.
- [ ] Completed linked documents plus valid completion metadata allow `kanban_complete`.
- [ ] Regression coverage exercises the actual completion hook seam.
- [ ] `make lint` and `make test` pass.

## Design constraint

Do not mark documents completed after the card is already done. Document finalization must happen before successful completion so the recorded artifact baseline includes final document state.

## Non-goals

- Automatically finalizing unrelated files.
- Changing Hermes core Kanban semantics.
- Bypassing `ginflow-gate` completion validation.

## Status

Card is blocked until explicitly selected for implementation.
