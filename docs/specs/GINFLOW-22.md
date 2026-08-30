---
status: completed
size: M
scope: project-local Ginflow validation and routing diagnostics
owner: ginb
---

# Spec — Harden project-context validation and routing diagnostics

## Objective

Make project-local Ginflow context fail closed with precise diagnostics while preserving the first-use initialization contract and atomic persistence guarantees.

## Contract

- `.ginflow.yaml` is the only project-local context file. Production code must not read, migrate, or write `.hermes/ginflow.yaml`.
- A configured `ginflow.workspace` must be an absolute path. A relative value is invalid even if resolving it would equal the current project directory.
- Routing distinguishes three project-context states: missing, invalid, and valid. Missing and invalid states block mutation and include actionable `/ginflow` initialization or repair guidance. A valid config with no cards for the configured workspace remains a no-card work-shaping route, not a configuration error.
- First-load initialization is agent-procedural: the `/ginflow` skill invokes the project-context initializer, presents the current/default-board versus new-board choice, performs native board creation before persistence when requested, and persists only complete context. Runtime helpers enforce validation and write ordering but do not add a CLI or silently initialize.
- Atomic persistence removes temporary files after write or replace failures and never leaves a partial `.ginflow.yaml`.

## Scope

Implementation is limited to `skills/ginflow/lib/project_config.py`, `plugins/ginflow-gate/routing.py`, focused regression tests, and Ginflow project-context documentation.

## Acceptance tests

- Relative workspace values are rejected with a clear invalid-workspace diagnostic.
- First-load current-board and new-board invocation behavior, including failure-before-persistence, is covered.
- Routing output names missing versus invalid context and gives exact remediation while keeping `mutation_allowed=False`; valid context with no workspace cards reports no cards.
- Atomic-write failures leave neither a partial config nor a temporary file.
- `make lint` and `make test` pass.

## Boundaries

No Ginflow CLI, Hermes global configuration changes, legacy `.hermes/ginflow.yaml` migration, or unrelated workspace-drift changes.

**Status: in_progress** — contract is being implemented and verified.
