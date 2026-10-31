---
status: active
scope: Herdr Hermes plan picker
owner: gintary
---

# HERDR-1 execution plan

1. Correct workspace routing to user-selected repository; select scoped
   Harness card and retain immutable execution package/batch in card history.
2. Add `plugins/herdr-hermes-plans/herdr-plugin.toml` and Python popup runner.
   Capture agent before opening; validate selected file and target before
   submitting; test with fake Herdr CLI and terminal input.
3. Add runnable check, plugin README, and Makefile verification entry.
4. Run `make lint && make test`; record exact outcomes and changed files on
   card. Keep completion blocked if baseline suite failure remains.

Baseline: `a756afb5b28f3c8a05e73a14cd6ae843703c5045`.
`make lint`: exit 0. `make test`: exit 2 at existing Ginflow gate test.
No automatic worker dispatch or publication is authorized by this plan.

## Implementation evidence

Selected Harness card: `t_106e1744`, assigned to `gintary`, blocked by full
repository verification. Immutable package and `HERDR-PLAN-PICKER/run-1`
authorization are recorded in its comments.

Implemented native popup, preview, selection/cancellation, literal prompt
delivery, file validation, target identity guards, runnable check, and usage
documentation under `plugins/herdr-hermes-plans/`. Makefile includes the
check in `plugin-test`; `.ginflow.yaml` targets this workspace.

- `make herdr-plan-test`: exit 0. Exercises actual manifest launch commands,
  real pseudo-terminal input, and fake Herdr responses; no live agent input.
- `make lint`: exit 0. Existing `/bin/sh: compgen: not found` warning remains.
- `make test`: exit 2 at existing `test_live_tmp_project_card` in
  `plugins/ginflow-gate/test_ginflow_gate.py`.
- Isolated reproduction of `hermes kanban init`: exit 1. Hermes bootstraps
  dependencies for a temporary home; `python-olm` build fails because
  `clang++` is missing. No unrelated test or runtime repair attempted.
- `herdr plugin link <plugin-directory> --enabled`: native manifest accepted.
  `herdr plugin action list --plugin gin.hermes-plans` lists `pick`.
- Native CLI probe against nonexistent target confirms dash-prefixed plan
  text is accepted as a positional argument; `--` separator is unsupported.
- `git diff --check`: exit 0.

No live popup-to-agent delivery claim. No completion commit or artifact
completion baseline recorded. Next: repair Hermes test bootstrap separately,
rerun `make lint && make test`, then verify live picker with an idle agent.
