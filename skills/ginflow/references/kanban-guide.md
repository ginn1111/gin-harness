# Kanban guide

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

For project work, use target-repo drift detection first.
After setup-repo updates, use setup repo `scripts/verify.sh` only for profile drift.
