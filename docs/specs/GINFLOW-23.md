---
status: completed
size: S
scope:
  - plugins/ginflow-gate/gate.py
  - completion-gate and artifact-guidance tests
  - skills/ginflow canonical instructions and templates
owner: ginb
---

# GINFLOW-23 — Frontmatter-only linked artifact lifecycle

## Objective

Make linked Ginflow Markdown artifact lifecycle validation use YAML frontmatter as its sole authority.

## Contract

- A linked brief, spec, or plan must begin with YAML frontmatter at byte 0.
- The frontmatter must parse as a mapping and declare `status: completed`.
- Missing, malformed, absent, or non-completed frontmatter blocks completion with actionable guidance.
- Body status prose, including stale or contradictory `**Status: ...**` lines, is ignored.
- A final body status line is not required.

## Acceptance criteria

- Frontmatter-only completed artifacts pass linked-document lifecycle validation.
- Body-only status text fails validation.
- Missing, malformed, and non-completed frontmatter fail validation.
- Completed frontmatter passes with contradictory body status text.
- Canonical instructions and validation messages require frontmatter status only.
