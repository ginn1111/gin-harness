---
status: draft
size: L
scope: PDOC-21
owner: ginb
---
# Plan — PDOC-21

1. Tests first: strict config validation (types, unknown fields, provider enum, status map completeness).
2. Implement `documents_error` and loader in `project_config.py`, preserving unrelated keys.
3. Adaptive resolver with precedence and conflict/no-evidence stops; report struct.
4. Target validation (GitHub repo, origin parse; Linear injected resolver).
5. Migration: preview diff, approval gate, timestamped backup in ignored state, atomic write.
6. Readiness reporting seam with injected checker; fail-closed message.
7. Add `.ginflow/` to ignore if missing; wire `test-document-config.py` into `Makefile` `lifecycle-test`.
8. `make lint && make test`; mark docs completed; commit scoped files.

Risks: `project_config.py` has uncommitted #26 changes (`notify`) in the worktree; use an isolated worktree off `develop`.
