# Ginflow linked-artifact worktree repair

Use when Ginflow blocks card because `Links:` path is missing from assigned worktree.

## Guardrails

- Treat task row, card body, target `AGENTS.md`, linked artifacts, and Git history as authority.
- One active card per mutable workspace. Finish repair card before unblocking original card.
- Do not edit original card body, invent acceptance criteria, change assignee, alter product repos, or silently advance a completion baseline.
- `hermes kanban edit` cannot repair a live card body.

## Repair sequence

1. Read original card with `hermes kanban show <task-id> --json`.
2. Confirm exact `Links:` path and assigned absolute worktree path.
3. Create separate repair card for same workspace. Keep original card blocked. Scope repair to exact missing artifact.
4. In assigned worktree, restore exact path from authoritative branch/history. Create artifact only when no authoritative copy exists and card provides enough requirements.
5. Stage and commit only linked artifact plus card-scoped changes. Do not include unrelated dirty files.
6. Run target canonical verification, then Ginflow harness against original card:

   ```bash
   python3 /home/aioz/.hermes/profiles/gintary/skills/ginflow/scripts/validate-harness.py \
     --setup-repo /home/aioz/personal/gin-harness \
     --target <assigned-worktree> \
     --kanban-task-id <original-task-id> --json
   ```

7. Record commit, commands, results, and remaining risk on repair card. Complete or release repair card first.
8. Re-read original card. If worktree is free and harness passes, unblock original card. Otherwise keep it blocked with exact repair step.

## Completion baseline

This repair commit restores dispatch readiness. It does not change original card completion metadata. Only original worker may create its completion baseline after acceptance criteria and canonical verification pass. Record exact linked paths; never substitute file hashes or silently replace commit.

## Failure handling

| Failure | Action |
| --- | --- |
| Linked path unclear | Keep original blocked. Ask human to repair card body in dashboard. |
| Artifact exists elsewhere but differs | Keep blocked. Ask human to classify source authority. |
| Unrelated worktree changes | Do not commit them. Isolate exact artifact or ask human. |
| Harness fails after artifact restore | Keep blocked. Record command output and next repair step. |
| Repair card still running | Do not unblock original; same workspace would collide. |
