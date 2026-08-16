---
status: ready
size: S
scope: ginflow next-card startup validation
owner: ginb
---

# Brief — GINFLOW-9 Validate linked documents before execution

## Objective

Validate linked target-local task documents before a Hermes `todo` or `ready` card can route to execution.

## Scope

- `plugins/ginflow-gate/routing.py`
- `skills/ginflow/lib/harness_core.py` only if shared startup validation requires changes
- `plugins/ginflow-gate/test_ginflow_gate.py`
- `skills/ginflow/scripts/test-harness-core.py`
- This brief

## Acceptance criteria

- [ ] Hermes `todo` and `ready` cards route through `validate_card_docs` before execution.
- [ ] Missing, malformed, outside-workspace, or changed linked documents produce deterministic safe validation routes.
- [ ] Valid linked documents produce `ready_to_start` guidance.
- [ ] Validation does not mutate card status or linked documents.
- [ ] Regression coverage exercises the actual `pre_llm_call` routing seam.
- [ ] `make lint` and `make test` pass.

## Design constraints

- Fail closed on unavailable or invalid evidence.
- Keep workspace paths canonical and target-local.
- Hermes Kanban remains the status authority.

## Provenance

Corrected independent replacement for malformed card `t_d228a0f2`, created with explicit human approval.

## Verification

Canonical commands: `make lint` and `make test`.
