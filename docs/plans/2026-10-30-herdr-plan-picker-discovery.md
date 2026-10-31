---
status: superseded
scope: Herdr plugin for selecting Hermes plans and sending them to an agent pane
owner: TBD (user-selected Kanban assignee)
---

# Herdr plan picker

## Confirmed request

Use `/home/aioz/personal/gin-harness` as target repository. Open a popup,
pick a Hermes plan, and send it to the active pane containing an agent.

## Discovered integration

- Installed `herdr` supports workflow plugins and native `popup` panes.
- Plugin invocation context includes `focused_pane_id` and
  `focused_pane_cwd`. Capture the target before opening the popup.
- `herdr agent prompt` supports submitting text to an agent by pane ID;
  it rejects recognized approval/question dialogs. Submission success
  does not prove execution completed; never automatically retry delivery.
- Installed Hermes catalog describes Plan Mode files under the session
  workspace's `.hermes/plans/`, with approved snapshots under `approved/`.
- Ginflow also stores implementation plans under `docs/plans/`.
- Harness board has no matching picker card. Existing cards concern Ginflow v2.
- `.ginflow.yaml` names board `harness` but contains a macOS workspace path.
  User selected this Linux workspace; reconcile the path before execution.

Evidence: `herdr --help`, `herdr --skill`, installed native popup manifest
for `chmarax.herdr-nvim`, installed Hermes `plugin-catalog/plan-mode.yaml`,
and `hermes kanban --board harness list --json`.

## Resolved product decision

User confirmed Herdr and Hermes Plan Mode files in `.hermes/plans/`.
Current contract: [HERDR-1](../specs/HERDR-1.md).

## Proposed behavior

Native popup with keyboard selection and cancellation. List plans from the
chosen source for the invoking workspace. Submit selected plan contents once
to the captured agent pane; closing the popup restores focus. Cancel sends
nothing. Missing plans, unreadable files, missing agents, changed occupants,
and blocked agents produce explicit errors without shell input fallback.

Prefer native popup plus Python standard library. An external terminal picker
adds a dependency; changing Herdr itself adds an upstream maintenance burden.

## Proposed scope and verification

Add a self-contained plugin under `plugins/`, installation instructions, and
one runnable check covering selection, cancellation, stable target identity,
input validation, and delivery failures using a fake Herdr command. Wire the
check into repository verification. Verify with `make lint && make test`;
live popup and delivery verification requires a suitable agent pane.

## Next step

Follow [HERDR-1 execution plan](HERDR-1.md). This document records discovery;
the linked contract and selected Kanban card govern execution.
