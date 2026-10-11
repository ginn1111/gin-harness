---
status: in_progress
size: M
scope:
  - plugins/ginflow-gate/ block routing for kanban_task_blocked
  - skills/ginflow/lib/project_config.py notify.target validation
  - plugins/ginflow-gate/ block routing test and Makefile plugin-test target
owner: ginb
---

# GINFLOW-26 — Critical kanban_block pushes to configured notify target

Refs: ginn1111/gin-harness#26 (parent spec), #27 (this slice).

## Objective

With `ginflow.trace: true` and a valid `ginflow.notify.target`, a worker `kanban_block` of kind `needs_input` or `capability` must send one bounded message through `hermes send` and leave the task `blocked`. This slice also lays the shared base for later routing slices: the trace gate, the `kanban_task_blocked` hook registration in `ginflow-gate`, and a stub-`hermes` test fixture.

## Contract

- **B1 Activation.** Routing must run only when the project's `.ginflow.yaml` has `ginflow.trace: true`. With trace off, `kanban_block` must behave natively: no send, no routing.
- **B2 Trigger.** Routing must run on the Hermes `kanban_task_blocked` lifecycle hook, registered by `ginflow-gate`. The hook is observer-only and its payload omits the kind. Routing must read `block_kind` from the task. A routing failure must not break the block transition.
- **B3 Critical kinds.** `needs_input` and `capability` must be routed as critical. Critical means push and stay `blocked`. The task must not be auto-resumed.
- **B4 Dependency.** `dependency` must pass untouched. Hermes already routes it to `todo`.
- **B5 Message.** The push must be one `hermes send` call to `ginflow.notify.target`. The body must be bounded and sanitized and must contain the task ID, the reason, the required action, the worker profile, and the run ID.
- **B6 Process.** `hermes send` must run under the worker's own profile. The target platform needs credentials in that profile.
- **B7 Config.** `.ginflow.yaml` gains an optional `ginflow.notify.target`, a string in the `hermes send --to` format. A wrong type, an empty value, or an unknown field under `notify` must make routing report an invalid project config. It must not break unrelated reads. A missing `notify` block is valid.
- **B8 Un-typed or other kinds.** Out of this slice: the guard (#28), the fallback chain (#29), `transient` repair (#30), and repeat escalation (#32). This slice must not change behavior for them.

## Behavior in this slice

When `notify.target` is absent or the push fails, this slice does only what is cheap and safe: leave the task `blocked`. The full fallback chain (native subscriptions, card comment) belongs to #29.

## TBD

- **Reason parsing for `required_action`** — owner: #28. This slice sends the raw sanitized reason and does not parse the field.
- **Exact message wording** — owner: ginb. It must satisfy B5 only.

## Acceptance criteria

- [ ] Critical block with valid target sends one `hermes send` with the bounded message and the task remains `blocked` (B3, B5)
- [ ] Trace off: no send, no routing, native `kanban_block` behavior (B1)
- [ ] `dependency` block is untouched (B4)
- [ ] Invalid `notify.target` reports an invalid project config route (B7)
- [ ] Hook failure does not break the block transition (B2)
- [ ] New test is wired into the `plugin-test` target
- [ ] `make lint && make test` pass

## Verification

Tests drive the `ginflow-gate` registered hooks through `register(ctx)` on a temp Kanban board with isolated `HERMES_HOME`. A stub `hermes` first on `PATH` records `send` calls and forwards every other subcommand to the real `hermes`. Prior art: `plugins/ginflow-gate/test_native_review_transition.py`.
