# Spec — Strict ginflow-gate routing module workspace-aware routing

## Problem

`ginflow-gate` routing module currently summarizes board state but does not safely distinguish cards belonging to different workspaces. It can also provide only advisory text when an explicit task is supplied. A worker may therefore resume the wrong card or begin implementation without clear orchestration selection.

## Desired behavior

On `pre_llm_call`, when `ginflow` is active, routing should:

1. Resolve current workspace with `Path.cwd().resolve()`.
2. Load Kanban cards from the current board.
3. Normalize card workspace values, including `dir:` paths.
4. Filter candidates to the current workspace.
5. Require explicit `HERMES_KANBAN_TASK` for implementation routing.
6. Return a deterministic structured route and concise context.
7. Report candidate cards to human/orchestrator when selection is ambiguous.
8. Block implementation guidance for unsafe or incomplete states.

Route values:

```text
needs_card_selection
no_cards_for_workspace
workspace_mismatch
blocked_card
terminal_card
validate_card_docs
docs_invalid
docs_changed
validation_failed
ready_to_start
transition_failed
```

Expected state behavior:

```text
no matching cards              → no_cards_for_workspace
multiple matching cards        → needs_card_selection
explicit task, wrong workspace→ workspace_mismatch
blocked selected card          → blocked_card
Hermes `todo`/`ready` card     → validate_card_docs
Hermes `running` valid card    → ready_to_start
terminal selected card         → terminal_card
```

Ginflow logical states map onto Hermes Kanban states: `next` means Hermes `todo` or `ready`; `in_progress` means Hermes `running`. Linked-document validation runs before `ready → running` claim. The transition test uses real Hermes Kanban `unblock`/`claim` operations.

## Inputs / outputs

Inputs:

- `HERMES_TUI_SKILLS`
- `HERMES_KANBAN_TASK`
- process current working directory
- `hermes kanban list --json` output
- selected card data when explicit task context exists

Output when `ginflow` is inactive:

```text
None
```

Output when active:

```json
{
  "context": "[ginflow-gate routing module: ...]"
}
```

The context must identify route, current workspace, candidate/selected card IDs where relevant, mutation guidance, and orchestrator action when required. It must not claim that document validation or status transition occurred unless those operations actually ran.

## Constraints

- Never auto-select by status, recency, title, assignee, or list order.
- Never select a card from another workspace.
- Never switch workspace silently.
- Cards from other workspaces are excluded from worker candidates.
- Routing remains ephemeral and must not persist context to session history.
- Hermes Kanban owns persisted status and claim lifecycle.
- Keep generated files and `__pycache__` out of changes.

## Acceptance criteria

- [ ] Workspace filtering uses canonical resolved paths.
- [ ] `dir:` workspace values compare correctly.
- [x] Multiple current-workspace cards produce `needs_card_selection`.
- [ ] Explicit cross-workspace task produces `workspace_mismatch`.
- [ ] Blocked and terminal statuses produce correct routes and block guidance.
- [ ] Hermes `todo`/`ready` produces `validate_card_docs`.
- [ ] Valid Hermes `running` produces `ready_to_start`.
- [ ] Real temporary card validates linked docs before `ready → running`.
- [ ] Missing/invalid Kanban output produces deterministic `validation_failed` or `no_cards_for_workspace` behavior without unsafe execution guidance.
- [ ] No-ginflow remains a no-op.
- [x] Tests cover all route branches and context output.
- [x] `make lint` passes.
- [x] `make test` passes.

## Edge cases

- Kanban CLI missing, timeout, non-zero exit, empty output, or malformed JSON.
- Card has missing, malformed, relative, or non-directory workspace.
- Explicit task ID is missing, unknown, terminal, blocked, or assigned to another workspace.
- Current workspace has no cards but board contains cards elsewhere.
- Current workspace has one or more cards but no explicit selection.
- Card status is unknown.
- `HERMES_TUI_SKILLS` contains multiple skills with commas or newlines.
- Workspace path includes symlinks; comparison uses resolved paths.

## Testing decisions

Test the highest existing seam: the plugin hook/helper behavior with subprocess and environment inputs controlled by test fixtures. Assert external behavior: route, candidate IDs, mutation guidance, and injected context. Avoid testing private implementation shape beyond observable routing behavior.

Use existing deterministic script style in `plugins/ginflow-gate/test_ginflow_gate.py`. Retain no-skill and active-skill coverage; add workspace, explicit-selection, status, malformed-input, and context assertions.

Verification commands:

```bash
make lint
make test
```

## Out of scope

- New Hermes core APIs or status names.
- Capability tokens.
- Mutation authorization.
- Audit logs.
- Automatic card creation, selection, workspace switching, or deployment behavior.

## Further notes

This spec supersedes earlier advisory-only routing assumptions for workspace/card selection. Routing reports state and intent; orchestration owns selection; Hermes core owns enforcement.

---
**Status: completed** — linked card `t_be3de2b6`.
