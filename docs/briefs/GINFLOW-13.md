# GINFLOW-13 — Map Gin-harness sections to plugin, core, or skill ownership

**Status: completed**

## Objective

Map each Gin-harness system section to its implementation ownership layer in the architecture diagram.

## Scope

- Inspect both pages in `docs/architecture/gin-harness-system.drawio`.
- Trace sections to `plugins/`, `skills/`, `skills/ginflow/lib/`, and shared setup docs.
- Add ownership labels: plugin, core, skill, shared, missing, proposed.
- Preserve red/green/yellow coverage colors and both pages.
- Add ownership legend.

## Acceptance criteria

- Every relevant section has evidence-based ownership mapping.
- Diagram distinguishes plugin, core, skill, shared, missing, and proposed ownership.
- Existing coverage colors remain accurate.
- Both pages remain readable and structurally intact.
- XML parse passes.
- `make lint && make test` passes.

## Verification

- Parse diagram XML and confirm two pages remain present.
- Check ownership labels and legend in target page(s).
- Run `make lint && make test`.
- Review diff for diagram and linked brief scope.

## Out of scope

- Moving code between plugin, core, and skill directories.
- Changing runtime behavior or profile configuration.
- Redesigning unrelated diagram pages.

**Status: completed**

**Verification: `make lint && make test` passed; diagram XML parse passed with two pages and ownership labels.**
