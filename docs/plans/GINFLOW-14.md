# Plan — GINFLOW-14 documentation alignment

**Status: completed**

## Goal

Make Gin-harness understandable from its repository documentation without changing runtime behavior.

## Evidence-first execution

1. Inspect local rules, the existing README, architecture diagrams, Ginflow skill, core, plugin, scripts, Makefile, and tests.
   - Evidence: completed during task startup; primary anchors are listed in `docs/briefs/GINFLOW-14.md`.
2. Define the documentation contract and explicit unknowns.
   - Evidence: `docs/specs/GINFLOW-14.md`.
3. Update the README with purpose, problem statement, architecture, dependency inventory, user flow, limitations, and pros/cons.
   - Evidence: `README.md`.
4. Add an architecture/dependency/gap reference that traces claims to implementation paths and separates intentional boundaries from missing or unknown behavior.
   - Evidence: `docs/architecture/gin-harness-reference.md`.
5. Keep the existing Draw.io diagrams and derived flow consistent; parse all diagram XML after edits.
   - Evidence: Python XML parse output.
6. Run project-native verification and review the diff against scope.
   - Commands: `make lint`; `make test`; `git diff --check`; `git status --short`.
7. Mark all linked artifacts completed only after verification passes, commit the linked artifacts and intended documentation changes, then provide matching completion metadata to the native Kanban completion tool.

## Non-goals

- Runtime implementation changes.
- Global Hermes profile/configuration changes.
- Secret or generated-file cleanup.
- Rewriting unrelated local changes.

## Risks and limits

- Hermes Agent internals are external to this repository; document the integration boundary rather than inferring implementation details.
- No committed package manifest was found, so exact dependency versions remain an explicit unknown.
- Existing unscoped working-tree changes must remain untouched and separately reported.

**Status: completed**
