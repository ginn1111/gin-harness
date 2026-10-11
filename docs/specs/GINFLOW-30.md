---
status: in_progress
size: S
scope:
  - plugins/ginflow-gate/routing.py pre_llm_call context extension and test
owner: ginb
---

# GINFLOW-30 — Repair worker gets error-origin context

Refs: ginn1111/gin-harness#26 (parent spec), #31 (this slice). Shared contract: `docs/specs/GINFLOW-26.md` (B1 to B8) and issue #26.

## Objective

The repair worker's prompt is told the error came from the worker, with profile, run ID, kind and reason.

## Contract

- When the running task has a worker-origin block comment, the pre-LLM-call context **must** include a bounded line with profile, run ID, kind and reason.
- Injection **must** fire only when the Kanban task environment matches that task.
- Content **must** stay bounded and sanitized.

## Acceptance criteria

- [ ] Matching task: context line present with profile, run ID, kind, reason
- [ ] Non-matching task: no injection
- [ ] No worker-origin comment: no injection
- [ ] Context bounded and sanitized
- [ ] `make lint && make test` pass
