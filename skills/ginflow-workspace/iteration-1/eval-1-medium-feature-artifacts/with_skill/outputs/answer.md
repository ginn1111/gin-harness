# INV-21 build-ready handoff

Work mode: implementation. Size M requires brief and plan. No spec or ADR: behavior has no separate contract or durable architecture decision needing its own artifact.

## `docs/briefs/INV-21.md`

```markdown
---
status: draft
size: M
scope: invoice list CSV export
owner: gintary
---

# Brief — INV-21 invoice list CSV export

## Objective
Enable users of the existing invoice list to download that list as CSV.

## Scope
- Add a CSV export action to the existing invoice-list experience.
- Export invoice-list headers and row values in the list's current order.
- Produce valid CSV when values contain commas, quotes, or line breaks.
- Add focused automated coverage for export behavior and invoice-list integration.

## Acceptance criteria
- [ ] From the invoice list, a user can trigger one CSV download.
- [ ] Downloaded CSV contains one header row and one data row per invoice in the exported list, preserving displayed row order.
- [ ] Exported headers and values correspond to invoice data represented by the existing list.
- [ ] Values containing commas, quotes, or line breaks are escaped as valid CSV.
- [ ] An empty invoice list exports a valid header-only CSV.
- [ ] Existing invoice creation behavior remains unchanged.
- [ ] `make test` passes.

## Non-goals
- Changing invoice creation, persistence, or validation.
- Adding new invoice fields or changing invoice-list contents.
- Adding import, spreadsheet formats, scheduled exports, or background export jobs.
```

## `docs/plans/INV-21.md`

```markdown
# Plan — INV-21 invoice list CSV export

1. Inspect invoice-list UI/controller, its current data source and ordering, existing download conventions, and relevant tests; record exact target files and confirm brief criteria map to existing list data. Evidence: target-file list and passing pre-change `make test` baseline. Covers scope boundary and invoice-creation non-goal.
2. Add focused failing tests at the existing invoice-list/export test boundary for download availability, header and row mapping, row order, header-only empty output, and CSV escaping. Evidence: new tests fail for missing export behavior. Covers acceptance criteria 1–5.
3. Add the smallest CSV export path within the existing invoice-list boundary, using project-native or standard-library CSV support and existing response/download conventions. Do not modify invoice-creation paths. Evidence: focused export tests pass. Covers acceptance criteria 1–6.
4. Review the diff for changes outside invoice-list export and tests, then run `make test` from `/work/invoice-app`. Evidence: scoped changed-file list plus exact fresh command result recorded on INV-21. Covers acceptance criteria 6–7.
```

## Kanban card `INV-21`

```text
Title: Add CSV export to invoice list

Objective:
- Let users download the existing invoice list as CSV.

Scope:
- Invoice-list export and focused tests only; invoice creation must not change.

Acceptance:
- Invoice list downloads as valid CSV, including headers, ordered invoice rows, escaped special characters, and header-only empty-list output; `make test` passes.

Workspace:
- dir:/work/invoice-app

Artifact links:
- docs/briefs/INV-21.md
- docs/plans/INV-21.md

Status:
- Ready for ginb
```
