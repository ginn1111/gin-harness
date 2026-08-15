# Merge ginflow-routing into ginflow-gate

Objective: simplify installation by shipping one public plugin.

Scope:
- Merge routing and completion gate behavior under `ginflow-gate`.
- Keep routing and gate logic separate.
- Update setup, Makefile, tests, docs, and architecture diagram.

Acceptance:
- `ginflow-gate` registers `pre_llm_call`, `pre_tool_call`, and `post_tool_call`.
- Standalone `ginflow-routing` is removed.
- `make lint && make test` passes.
- Related docs use `ginflow-gate` naming.

Links:
- `docs/specs/GINFLOW-GATE-MERGE.md`

Status: completed.
Verification: `make lint && make test`; draw.io validation; `git diff --check`.
Commit baseline recorded on Kanban card.
