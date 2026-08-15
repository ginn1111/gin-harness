---
status: active
size: M
scope: setup-repo
owner: ginb
---

# Brief — Strict ginflow-routing workspace-aware routing

## Objective

Make `ginflow-routing` route worker sessions safely when one Kanban board contains cards for multiple workspaces. The worker must report candidate cards to human/orchestrator authority and must not infer or auto-select implementation work.

## Scope

- Resolve current workspace with `Path.cwd().resolve()`.
- Normalize card workspace values, including `dir:` paths, before comparison.
- Filter board cards to current workspace.
- Require explicit `HERMES_KANBAN_TASK` for execution routing.
- Return deterministic routes for card selection, workspace mismatch, blocked/terminal cards, document validation, and valid resumption.
- Use Hermes Kanban states as persistence source: Ginflow `next` maps to `todo`/`ready`; Ginflow `in_progress` maps to `running`.
- Validate linked docs before `ready` cards are claimed into `running`.

## Acceptance criteria

- [ ] Cards from other workspaces do not affect current worker routing.
- [ ] Multiple cards in current workspace produce `needs_card_selection`; routing reports candidates and blocks implementation.
- [ ] Explicit task from another workspace produces `workspace_mismatch` and blocks implementation.
- [ ] A blocked card produces `blocked_card` and reports orchestrator action required.
- [ ] Hermes `todo`/`ready` cards produce `validate_card_docs` before claim.
- [ ] Hermes `running` cards produce `ready_to_start`.
- [ ] Terminal cards produce `terminal_card` and block implementation.
- [ ] Routing output is structured and deterministic.
- [ ] Existing and new routing tests pass with `make lint` and `make test`.

## Non-goals

- Hermes-core Kanban transaction/API changes.
- Capability-token issuance or validation.
- Mutation-tool enforcement.
- Audit-log design.
- Automatic card selection or workspace switching.

## Notes

The worker reports candidate cards; human/orchestrator selects the task through explicit task context. Routing provides guidance and state; hard mutation enforcement belongs to Hermes core.
