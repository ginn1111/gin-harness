# INV-21 build-ready handoff

Work mode: implementation. Size M. Proposed artifacts live in target repo `/work/invoice-app`. CSV behavior can drift, so use brief + spec + plan. No session handoff or ADR needed.

## `/work/invoice-app/briefs/INV-21.md`

```markdown
---
status: ready
size: M
scope: existing invoice list and CSV export
owner: ginb
---

# Brief — Add CSV export to invoice list

## Objective
Allow users to export invoices currently represented by existing invoice-list behavior as a CSV file.

## Scope
- Add CSV export entry point to existing invoice list.
- Reuse existing invoice-list query/filter/sort behavior for exported rows.
- Add focused export tests and preserve existing invoice-list tests.

## Acceptance criteria
- [ ] Invoice list offers a CSV export action.
- [ ] Export returns a downloadable `.csv` file with one header row and one row per invoice in current list result.
- [ ] Exported columns, ordering, escaping, empty-result behavior, and filename match `specs/INV-21.md`.
- [ ] Active invoice-list filters and ordering apply to export.
- [ ] Existing invoice creation behavior and tests remain unchanged.
- [ ] `make test` passes from `/work/invoice-app`.

## Non-goals
- Changing invoice creation.
- Adding new invoice fields, imports, background jobs, or alternate export formats.
- Redesigning invoice-list filtering, sorting, or pagination.

## Notes
Canonical verification: `make test`.
```

## `/work/invoice-app/specs/INV-21.md`

```markdown
# Spec — Invoice-list CSV export

## Problem
Users can inspect invoices in the existing list but cannot download list data for spreadsheet or reporting use.

## Desired behavior
- Existing invoice list exposes an `Export CSV` action.
- Export uses the same authorization, filters, and sort order as the existing list.
- Export includes all rows matching current list criteria, not only the visible pagination page.
- Response downloads a CSV file; no invoice data is changed.

## Inputs / outputs
- Input: current invoice-list filter and sort parameters supported by the application.
- Output filename: `invoices-YYYY-MM-DD.csv`, using application date/time conventions.
- Header order: `Invoice ID,Customer,Issue Date,Due Date,Status,Total`.
- One data row per matching invoice, in invoice-list sort order.
- Dates use the list's existing date representation; totals use the list's existing display value without adding a currency symbol.

## Constraints
- Use the project's existing framework/standard-library CSV support; add no dependency solely for CSV generation.
- Emit valid CSV with a header row, UTF-8 text, and CRLF record separators.
- Quote/escape commas, quotes, and line breaks according to CSV rules.
- Apply existing invoice-list authorization and avoid a separate divergent query path where practical.
- Do not change invoice creation code, request handling, validation, persistence, UI, or API contract.

## Acceptance criteria
- [ ] Export response has CSV content type and attachment disposition with specified filename.
- [ ] Header names and order match this spec.
- [ ] Matching invoices export once each in current list order.
- [ ] Filters affect exported rows; pagination does not truncate them.
- [ ] Empty results produce header-only CSV.
- [ ] Fields containing commas, quotes, or line breaks round-trip as valid CSV.
- [ ] Unauthorized users receive existing invoice-list denial behavior.
- [ ] Existing invoice creation tests pass unchanged.
- [ ] `make test` passes.

## Edge cases
- No matching invoices: header only.
- Embedded comma, quote, newline, or non-ASCII text: valid escaped UTF-8 CSV.
- Missing optional display value: empty field, not literal `null`/`None`.
- Large result: follow existing project response conventions; streaming or async export is out of scope unless repository constraints require it.
```

## `/work/invoice-app/plans/INV-21.md`

```markdown
# Plan — INV-21 invoice-list CSV export

1. Read `AGENTS.md` / `.hermes.md`; inspect invoice-list route/controller, query/service, view, authorization, pagination, and existing tests. Run baseline `make test`.
2. Add failing focused tests for response headers, fixed column order, filtered/sorted full-result export, header-only empty export, CSV escaping/UTF-8, authorization, and unchanged invoice creation regression coverage.
3. Add the smallest export endpoint/handler by reusing invoice-list authorization and query/filter/sort logic while removing only pagination for export.
4. Generate CSV with existing framework or standard-library support and add the list's `Export CSV` action, preserving supported filter/sort parameters.
5. Review diff for scope: no invoice creation behavior or contract changes; no unrelated refactor or new dependency.
6. Run `make test` from `/work/invoice-app`. Record exact result and changed files on INV-21; complete only if all acceptance criteria pass.
```

## Kanban card `INV-21`

```text
Title: Add CSV export to existing invoice list

Objective:
- Let users download current invoice-list results as valid CSV.

Scope:
- Existing invoice-list UI/route, shared list query/filter/sort path, and focused tests.
- Do not change invoice creation behavior or contract.

Acceptance:
- CSV contract and edge cases in `specs/INV-21.md` pass.
- Existing invoice creation remains unchanged.
- `make test` passes from `/work/invoice-app`.

Workspace:
- dir:/work/invoice-app

Artifact links:
- briefs/INV-21.md
- specs/INV-21.md
- plans/INV-21.md
```

Handoff readiness: card states what/where/done/non-goal; brief owns scope and acceptance; spec fixes CSV contract; plan gives execution and canonical verification order.
