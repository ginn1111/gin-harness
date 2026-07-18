# Project rules

This project uses globally installed Hermes profiles sourced from your setup repo.
Global profile behavior lives there. Local project behavior lives here.
Shared workflow, Kanban lifecycle, verification evidence, and optional handoff rules come from `ginflow`.

## Build
- Run project-native verification before claiming done.
- Prefer existing scripts (`make`, `npm`, `pnpm`, `pytest`, etc.) over ad-hoc commands.

## Style
- Keep diffs small.
- Match existing code style and project structure.
- Do not add dependencies without need.

## Task shaping
- If requirement is clear: build.
- If cause is unclear: investigate first.
- If requirement is unclear: shape options first.

## Verification
- Leave real command output or concrete verification evidence.
- If verification is blocked, say exact blocker.

## Local notes
- Add project-specific build/test/run commands below.
- Add architecture constraints, forbidden areas, and deployment rules below.
- Add key directories, file/git conventions, and project-specific completion requirements below.

### Example additions
- `make test`
- `pnpm test`
- `pytest -q`
- `cargo test`
- `go test ./...`
- never edit generated files under `dist/`
- ask before production deploy
