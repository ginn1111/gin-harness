# GINFLOW-ROUTING-DECOUPLE

Objective: Extract routing policy into framework-agnostic `ginflow-core` while keeping Hermes integration in `ginflow-gate`.

Scope:
- Move workspace/card route decisions into `skills/ginflow/lib/routing.py`.
- Keep subprocess, environment, cwd, hook registration, and context formatting in `plugins/ginflow-gate/routing.py`.
- Preserve deterministic routing behavior and regression coverage.

Acceptance:
- Core routing has no Hermes/profile/env/subprocess dependency.
- Adapter delegates policy and preserves existing route behavior.
- Multiple cards never auto-select; no-card, blocked, terminal, invalid, and valid-card routes remain deterministic.
- `make lint && make test` passes.

Links:
- docs/specs/GINFLOW-ROUTING.md

---
**Status: completed** — linked card `t_a6b72183` is done.
