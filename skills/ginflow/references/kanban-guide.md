# Kanban guide

Thin card pattern:
- title
- 1-2 sentence objective
- scope
- acceptance
- link to artifact if present

Workspace rule:
- use real target repo
- `dir:/abs/path` for existing checkout
- `worktree` for isolated code changes

Do not leave project work in scratch workspace if files must be read from repo.

After setup-repo updates, use setup repo `scripts/verify.sh` to catch profile drift.
For project-specific workflow drift, add a separate `verify.sh` in target repo if needed.
