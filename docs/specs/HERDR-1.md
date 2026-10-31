---
status: active
scope: plugins/herdr-hermes-plans, Makefile, .ginflow.yaml
owner: gintary
---

# HERDR-1: Send a Hermes plan to the invoking agent

User confirmed Herdr, this repository as workspace, and workspace-local
Hermes Plan Mode files in `.hermes/plans/` as the source.

## Contract

- Open a native Herdr popup from a plugin action. Capture the invoking pane
  and its agent identity before opening it. Never retarget on focus changes.
- List Markdown files recursively under that agent's working directory's
  `.hermes/plans/`, including approved snapshots, with relative filenames.
- Arrow keys select; Enter submits the complete selected UTF-8 text once;
  Escape cancels without sending. Show the selected plan's text for inspection.
- Recheck agent session, terminal, and foreground process identity before
  submission. Reject missing, replaced, suspended, or non-idle agents.
- Use `herdr agent prompt`; never execute plan contents as shell commands.
- Reject escaped paths, symlinks, non-regular files, invalid UTF-8, empty
  plans, unsafe control characters, and plans larger than 64 KiB. Never
  truncate submitted text or automatically retry uncertain delivery.
- Errors remain visible in the popup. No runtime dependencies beyond Herdr
  and Python standard library. Linux and macOS supported.

## Boundaries

No Hermes approval bypass, plan edits, automatic task dispatch, upstream
Herdr changes, or changes to unrelated failing repository tests.

## Acceptance and verification

Runnable standard-library check must prove correct source and target,
cancellation, literal multiline delivery, invalid-file rejection, changed
agent rejection, and no retry on delivery failure. Check manifest and popup
keyboard flow. Canonical command: `make lint && make test`.

Baseline full suite fails in `plugins/ginflow-gate/test_ginflow_gate.py`:
temporary-project `hermes kanban init` exits 1. This is a completion blocker,
not permission to alter unrelated code. Baseline `make lint` passes.

Herdr 0.9.5 has no atomic compare-session-and-submit operation. Target checks
run immediately before its agent-aware prompt command; replacing or
suspending an agent during that gap remains a native API limitation.
