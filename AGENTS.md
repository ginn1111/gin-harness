# Setup-repo rules

## Ginflow
- Load and follow `ginflow` for target-project startup, task shaping, execution, completion, and handoff. `ginflow` is an external skill: discover it through normal skill-discovery (scan available skills, read its SKILL.md) rather than expecting its instructions to be duplicated here.
- If the `ginflow` skill cannot be located in the current environment, stop before any mutable target-project work and report this as a blocker. Do not proceed ungated.
- Do not use this setup repo as target-project workspace.
- Before mutable target-project work, require a selected Kanban card (Hermes Kanban) with objective, scope, acceptance, workspace, status, assignee, and links. Stop when missing or incomplete.

## Boundaries
- This repo owns shared integrations, Ginflow, harnesses, plugins, setup scripts, and target-project starter docs.
- Target repos own product code, tests, local `AGENTS.md` / `.hermes.md`, and task artifacts.
- Shared workflow and Kanban lifecycle come from `ginflow`.
- Do not edit profile distribution identity, secrets, runtime state, or generated `__pycache__/` files.

## Key directories
- `skills/ginflow/` — shared workflow, templates, validator, tests
- `core/ginflow-core/` — reusable Ginflow core library
- `plugins/ginflow-gate/` — blocking Kanban completion policy plugin (part of the ginflow ecosystem; validates required fields, evidence, baseline commit, and artifact drift at completion)
- `templates/` — target-project starter docs
- `scripts/` — setup integration scripts
- `.hermes/` — session-scratch artifacts (untracked, auto-generated)

## Verification
- Canonical command: `make test`. This is the single authoritative verify command for this repo.
- `make test` runs `lint`, `setup-test`, `harness-core-test`, `artifact-guidance-test`, `kanban-harness-test`, `ginflow-gate-test`.
- Run `make lint` before declaring docs or script changes done.
- Run target-project verification from target repo; do not substitute setup verification or Ginflow harness for it, and vice versa.

## Drift detection
- **Local authorities**: `AGENTS.md` (this file), `Makefile` targets, `README.md`, `INSTALL.md`.
- **Generated-file relationships**: `__pycache__/` is always derived and excludable. `.bin/` holds session-scratch artifacts; never commit or restore.
- **Remediation order**: run `make lint` → `make test` → confirm all targets pass before declaring drift resolved. If `make test` fails on non-own code, report blocker; do not fix silently.

## Git conventions
- `make test` must pass before push.
- `make lint` must pass before commit.
- Keep `__pycache__/` and `.bin/` in `.gitignore`; update `.gitignore` when new generated paths appear.
- Do not commit credentials, `.env`, profile identity, or runtime state.

## Completion
- For Ginflow Kanban work: the selected Hermes Kanban card is the single source of truth for status, evidence, and blockers — there is no separate escalation channel.
  - Record on the card: verification evidence, changed files, commit, and any blockers.
  - Blocker entries must include enough detail to act on: what failed, where, why it's out of scope to fix directly, and what's needed to unblock.
  - Run `make test` from the setup repo as the system check; run the target project's canonical command from the target repo for the product check.
  - The `ginflow-gate` plugin validates required fields, evidence, baseline commit, and artifact drift before allowing completion.
- For setup-repo changes (this repo): run `make lint && make test` and confirm all targets pass.
