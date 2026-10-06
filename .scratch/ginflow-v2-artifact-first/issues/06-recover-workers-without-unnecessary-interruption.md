# 06 — Recover workers without unnecessary human interruption

**What to build:** Give workers deterministic retry and exception behavior so recoverable work continues automatically while genuine blockers produce one complete, correctly classified handoff. Only a human decision or contract change interrupts Gin.

**Blocked by:** 05 — Run workers continuously until done or exception.

**Status:** ready-for-agent

- [ ] Retries continue while they produce new evidence or reduce failure scope.
- [ ] Retry exhaustion follows the approved three-fix, two-no-evidence, unavailable-dependency, and turn-budget thresholds.
- [ ] Exceptions route correctly to needs_input, dependency, capability, or transient handling.
- [ ] One structured handoff records completed work, blocker, evidence, attempts, files, verification, required decision, and resume step.
