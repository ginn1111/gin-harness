# Setup-repo rules

## Ginflow
- Load and follow `ginflow` for target-project startup, task shaping, execution, completion, and handoff.
- Do not use this setup repo as target-project workspace.
- Before mutable target-project work, require a selected Kanban card with objective, scope, acceptance, workspace, status, assignee, and links. Stop when missing or incomplete.

## Scope
- This repo owns shared integrations, Ginflow, harnesses, plugins, setup scripts, and target-project starter docs.
- Target repos own product code, tests, local `AGENTS.md` / `.hermes.md`, and task artifacts.
- Do not edit profile distribution identity, secrets, runtime state, or generated `__pycache__/` files.

## Verification
- Canonical command: `make test`.
- Run `make lint` before declaring docs or script changes done.
- Run target-project verification from target repo; do not substitute setup verification or Ginflow harness.
