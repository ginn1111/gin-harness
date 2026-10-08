---
status: completed
size: S
scope: Trace integration end-to-end (gate calls recorded under configured workspace)
owner: ginb
---
# TRACE-INT — Integration Trace

## Objective
Verify the opt-in `ginflow-trace` plugin records real Ginflow gate
function calls (`load_card`, `validate_completion`, `pre_tool_call`)
when driven by the full Kanban create → load → validate → complete
lifecycle.

## Scope
- `plugins/ginflow-trace/test_ginflow_trace_integration.py`
  drives the real `gate.py` functions against a real Kanban card on an
  isolated board (`gin-harness-testing`).
- Each gate call appends a JSON record to
  `<workspace>/.ginflow/logs/<session>__<task>.json`.

## Acceptance
- A single integration test exercises CREATE → LOAD → VALIDATE →
  COMPLETE (allowed) → COMPLETE (drift, blocked) under a workspace-
  rooted `.ginflow/` directory.
- All recorded events reference the real gate function name and
  succeed.
- `make trace-test` and `make test` both pass.

## Links
- `plugins/ginflow-trace/ginflow_trace/decorator.py` — trace decorator
  and workspace-rooted log resolution.
- `plugins/ginflow-trace/test_ginflow_trace.py` — unit tests covering
  workspace validation + no-fallback semantics.
- `plugins/ginflow-trace/test_ginflow_trace_integration.py` —
  end-to-end lifecycle test.
- `docs/specs/GINFLOW-21.md` — parent contract for the trace plugin.