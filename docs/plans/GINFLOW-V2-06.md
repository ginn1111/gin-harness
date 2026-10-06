---
status: approved
size: XL
scope: GINFLOW-V2-06
owner: ginb
---

# Plan — Recover workers without unnecessary human interruption

## Objective

Give workers deterministic retry and exception behavior so recoverable work continues automatically while genuine blockers produce one complete, correctly classified handoff. Only a human decision or contract change interrupts Gin.

## Dependencies

05 — Run workers continuously until done or exception.

## Execution

- Implement the smallest complete vertical slice described by this plan.
- Preserve version 1 behavior until the explicit contraction unit.
- Run project-native verification and record exact evidence on the Kanban card.

## Acceptance criteria

- [ ] Retries continue while they produce new evidence or reduce failure scope.
- [ ] Retry exhaustion follows the approved three-fix, two-no-evidence, unavailable-dependency, and turn-budget thresholds.
- [ ] Exceptions route correctly to needs_input, dependency, capability, or transient handling.
- [ ] One structured handoff records completed work, blocker, evidence, attempts, files, verification, required decision, and resume step.
