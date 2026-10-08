# Architecture

This directory documents the Gin-harness system and its Ginflow routing model.

## Sources and derived views

- [Canonical Draw.io architecture](./gin-harness-system.drawio) — source of truth, including the **Gin-harness system** and **Harness system overview** pages.
- [Ginflow mental model](./ginflow-flow.md) — GitHub-readable Mermaid documentation derived from the canonical Draw.io page.

Update Draw.io first when workflow behavior changes, then update the Mermaid explanation. Mermaid is derived documentation, not a second authority.

## Implementation boundaries

- [Ginflow skill and distributed harness core](../../skills/ginflow/) — shared workflow, routing, validation, artifacts, and verification guidance.
- [Ginflow routing core](../../core/ginflow-core/routing.py) — framework-agnostic routing primitives.
- [`ginflow-gate` plugin](../../plugins/ginflow-gate/) — routing-context injection and the blocking Kanban completion gate.
- [Work-size and output contract](../specs/GINFLOW-WORK-SIZE-OUTPUT-DOCS.md) — conditional Governance Artifact and Direct Work rules.
