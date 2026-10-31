---
status: draft
scope:
  - plugins/with-chatgpt/
  - INSTALL.md
  - docs/c2c-architecture.html
  - docs/specs/CHAT-1.md
owner: default
---

# CHAT-1 — Execution plan

1. Record passing repository baseline; authorize one immutable execution batch
   for the linked spec and selected card `t_09b79689` on board `harness`.
2. Simplify session storage and hook; remove protocol CLI and execution MCP
   surfaces, retaining read-only workspace access and historical local data.
3. Replace active collaboration skills and docs with plain-chat guidance;
   update focused integration tests for the smaller interface.
4. Run plugin checks, runtime tests/typecheck/build, and canonical repository
   verification. Record changed files, baseline, evidence, and limitations on card.

Stop on failing baseline outside scope, security regressions, or missing required
workflow context. Preserve pre-existing `.ginflow.yaml`,
`skills/ginflow/lib/harness_core.py`, and `take-note.md` changes.

## Startup evidence — blocked

- Card: `t_09b79689`, board `harness`, assignee `default`, status `blocked`.
- Source baseline: `a756afb5b28f3c8a05e73a14cd6ae843703c5045`.
- `make lint && make test`: exit 2. Lint, core tests, lifecycle tests,
  with-chatgpt plugin tests and plugin validation passed. Canonical suite stopped
  in `plugins/ginflow-trace/test_ginflow_trace_integration.py:78` because
  `hermes kanban init` returned exit 1.
- Isolated reproduction captured Hermes runtime preparation failing to download
  `ruamel-yaml==0.18.16` and `truststore==0.10.4`: DNS lookup for
  `files.pythonhosted.org` failed, including with elevated execution.
- No passing baseline, package authorization, or implementation changes yet.
  Restore dependency-download access, rerun baseline, then authorize batch and
  proceed with step 2. Do not change unrelated trace tests to hide failure.
