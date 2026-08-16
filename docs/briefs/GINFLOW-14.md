# GINFLOW-14 — Complete ownership mapping on Gin-harness-flow page

**Status: completed**

## Objective

Put implementation ownership mapping directly on the `Gin-harness-flow` page.

## Scope

- Add ownership labels to flow nodes.
- Keep red/green/yellow coverage colors.
- Add a readable ownership legend to `Gin-harness-flow`.
- Preserve `Harness system overview` unchanged.

## Acceptance criteria

- Flow page shows `plugin`, `core`, `skill`, `shared`, `missing`, and `proposed` ownership for relevant sections.
- Coverage colors remain accurate.
- Ownership legend is readable.
- Harness system overview page remains unchanged.
- XML parse passes.
- `make lint && make test` passes.

## Verification

- Parse diagram XML and confirm both pages remain present.
- Confirm ownership labels and legend on the flow page.
- Confirm the overview page is unchanged.
- Run `make lint && make test`.
- Review diff for diagram and linked brief scope.

## Out of scope

- Moving code between plugin, core, and skill directories.
- Changing runtime behavior or profile configuration.
- Redesigning unrelated diagram pages.

**Status: completed**
