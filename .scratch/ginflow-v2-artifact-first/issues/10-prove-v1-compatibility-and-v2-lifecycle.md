# 10 — Prove version 1 compatibility and version 2 lifecycle

**What to build:** Demonstrate the complete artifact-first lifecycle through the highest existing integration seam while proving that already-active legacy cards still follow version 1 rules. Make documentation, validator, plugin guidance, gates, review, drift handling, and lifecycle behavior pass together.

**Blocked by:** 08 — Reshape, cancel, and rebaseline active packages; 09 — Migrate related documentation.

**Status:** ready-for-agent

- [ ] The end-to-end lifecycle test covers Shaping output, blocked cards, validation, frontier release, dependencies, goal-mode work, exceptions, review, integration, drift, and completion.
- [ ] Active version 1 cards retain their existing lifecycle behavior.
- [ ] Focused tests cover validator and exception failures that are impractical to assert through the lifecycle seam.
- [ ] Canonical repository lint and full deterministic tests pass.
