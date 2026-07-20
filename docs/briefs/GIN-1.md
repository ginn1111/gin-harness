---
status: ready
size: XS
scope: setup-repo agent guidance
owner: gintary
---

# Brief — Require Ginflow for setup-repo agent guidance

## Objective

Ensure agents using this setup repo load and follow `ginflow` for target-project work.

## Scope

- Document Ginflow as required workflow in setup-repo guides.
- Make target-project starter require Ginflow for task lifecycle.

## Acceptance criteria

- [ ] Setup-repo guidance tells agents to use Ginflow for target-project startup, execution, completion, and handoff.
- [ ] Target-project starter requires a selected complete Kanban card before mutable work.
- [ ] Setup-repo and target-repo ownership boundary stays explicit.

## Non-goals

- Change Ginflow workflow, harness, or Kanban gate behavior.
- Add target-project-specific build commands.

## Notes

- Card: `t_73927675`.
- Canonical verification: `make test`.
- Links: `README.md`, `INSTALL.md`, `templates/AGENTS.md`.
