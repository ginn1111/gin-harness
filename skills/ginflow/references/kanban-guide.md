# Kanban guide

## Gate

Pre-card work may brainstorm, route, size, inspect read-only context, choose artifacts, and draft card content. Any target artifact creation, implementation investigation, code change, dispatch, progress, verification, completion, or handoff requires one selected card.

No selected card blocks execution. Selected card requires ID, title, objective, scope, acceptance, workspace, status, assignee, and links. Missing field blocks execution until repaired.

Thin card pattern:
- title
- 1-2 sentence objective
- scope
- acceptance
- link to artifact if present

Use card ID for linked artifacts:
- `docs/briefs/<CARD-ID>.md`
- `docs/specs/<CARD-ID>.md`
- `docs/plans/<CARD-ID>.md`

Before closing unfinished or blocked work, record outcome, changed files, verification, blockers, next step, and accurate status on card. Optional Markdown handoff export does not replace or mutate card.

Before completion, re-run canonical verification in target repo and derive changed-file evidence from target-repo `git status --short`. Temporary checks outside card workspace do not prove completion.

Workspace rule:
- use real target repo
- `dir:/abs/path` for existing checkout
- `worktree` for isolated code changes

Do not leave project work in scratch workspace if files must be read from repo.

Run target-declared project verification first. Run ginflow harness externally against target and selected card; never copy harness into target repo. Report project verification and harness result separately.
After setup-repo updates, use setup repo `scripts/verify.sh` only for profile drift.
