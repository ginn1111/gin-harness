# Spec — GINFLOW-14 documentation contract

**Status: completed**

## Problem

Gin-harness combines repository-local guidance, a shared Ginflow skill, a reusable core library, and a `ginflow-gate` plugin around Hermes Agent. Existing documentation explains important routing behavior, but a reader still needs to reconstruct the project purpose, component boundaries, dependency contract, and known gaps from several directories.

## Desired behavior

The project documentation must provide one consistent mental model grounded in repository evidence:

- Gin-harness is a setup/integration repository, not a product application.
- Hermes remains the runtime authority for profiles, skills, tools, Kanban, and lifecycle execution.
- Ginflow supplies workflow vocabulary and routing/validation guidance.
- `ginflow-gate` supplies integration hooks and completion enforcement; it does not replace Hermes or perform semantic classification.
- `core/ginflow-core` supplies reusable workflow primitives; target repositories own product code and canonical verification.
- Documentation must distinguish confirmed implementation from gaps, proposals, and unknown external behavior.

## Evidence contract

Each architecture or dependency claim must name an evidence path or an explicit external dependency boundary. Documentation must not claim an unobserved package manifest, runtime API, deployment topology, or production behavior.

## Required documentation coverage

### B1 — Purpose and problem

README must explain the problem of executing ambiguous or risky work without reliable scope, workspace, verification, and completion boundaries, and how Ginflow addresses that problem.

### B2 — Architecture and ownership

README and architecture documentation must map Hermes, Ginflow core, the `ginflow-gate` plugin, the `ginflow` skill, target projects, Kanban, and project verification to explicit ownership boundaries.

### B3 — Dependencies

Documentation must inventory repository-local dependencies and external/runtime dependencies, including the absence of a committed Python/package manifest where observed. Unknown versions or deployment details must be marked unknown rather than guessed.

### B4 — Current behavior and user flow

Documentation must describe startup, routing, governed execution, Direct Work eligibility, Clarification, verification, and completion at a level traceable to `skills/ginflow/SKILL.md` and `docs/architecture/ginflow-flow.md`.

### B5 — Gaps and trade-offs

Documentation must distinguish implementation-backed gaps from intentional boundaries and describe user-facing pros and cons without implying unsupported guarantees.

## Constraints

- Documentation-only change for this card.
- Do not modify runtime behavior, profile identity, secrets, generated files, or unrelated pre-existing local changes.
- Draw.io remains the editable authority for diagram pages; Markdown explanations are derived views.

## Acceptance criteria

- [x] B1–B5 are covered by README and linked documentation.
- [x] Claims include evidence paths or explicit unknowns.
- [x] Ownership boundaries and verification authority are unambiguous.
- [x] No runtime or profile behavior changes are introduced.
- [x] XML parsing, `make lint`, and `make test` pass.

## Edge cases and explicit unknowns

- The repository has no committed `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, or requirements file; exact transitive dependency versions are therefore runtime/environment concerns, not documented as fixed project dependencies.
- Hermes Agent internals and native Kanban implementation are external authorities; this repository documents its integration contract, not their complete source implementation.
- Optional CodeGraph/MCP health is advisory and must not be presented as a required runtime dependency.

**Status: completed**
