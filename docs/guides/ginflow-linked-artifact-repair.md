# Ginflow linked-artifact worktree repair

Use when Ginflow blocks an assigned card because exact `Links:` path is absent from assigned worktree.

## Guardrails

- Treat task row, card body, target `AGENTS.md`, linked artifacts, Git history, and approved source branch as authority.
- Keep original card blocked. Run one repair card in mutable workspace; never run repair and original cards together there.
- Different workspaces or isolated worktrees may run in parallel. Claim-time collision enforcement remains Hermes core responsibility.
- Do not edit original card body, invent acceptance, change assignee, alter product repos, or include unrelated dirty files.
- `hermes kanban edit` cannot repair live card body. Path or acceptance ambiguity needs dashboard repair by human.

## Repair order

1. Read original card. Confirm exact `Links:` path, objective, acceptance, status, and assigned absolute worktree.
2. Inspect target `AGENTS.md`, Git status, path history, and authoritative branch. Leave original card blocked.
3. Create repair card scoped to exact missing artifact and same worktree. Do not unblock original while repair card is active.
4. Restore exact path from authoritative history or branch:

   ```bash
   git restore --source <authority-commit-or-branch> -- docs/briefs/<CARD-ID>.md
   ```

   Create artifact only when no authoritative copy exists and original card gives enough requirements. Otherwise block repair card for human decision.
5. Inspect diff. Stage and commit only missing linked artifact plus repair-card-scoped files. Never commit unrelated worktree changes.
6. Run target canonical verification. Then run external Ginflow harness against original card from setup repo or deployed skill:

   ```bash
   python3 <setup-repo>/skills/ginflow/scripts/validate-harness.py \
     --setup-repo <setup-repo> --target <assigned-worktree> \
     --kanban-task-id <original-task-id> --json
   ```

7. Record repair commit, canonical command/result, harness command/result, and workspace warnings on repair card. Complete repair card first.
8. Re-read original card. Unblock only when repair card is complete, workspace has no active competing card, exact linked path exists, and harness passes. Otherwise keep original blocked with exact next step.

## Completion baseline boundary

Repair commit restores dispatch readiness only. It does not create, replace, or advance original card `artifact_baseline`.

Only original worker may create its completion baseline after original acceptance criteria and canonical verification pass. Record completion commit and exact linked paths in original completion metadata. Never use file hashes or silently replace baseline commit.

Completed-card drift needs human choice:

1. New intent: restore completed artifact, create versioned docs and follow-up card.
2. Changed completed scope: reopen, reconcile, verify, commit, and complete again.
3. Editorial-only: human explicitly approves baseline advance and approval note records it.

## Stop cases

| Condition | Action |
| --- | --- |
| Linked path or acceptance unclear | Keep original blocked. Human repairs card body in dashboard. |
| Artifact copies differ | Keep original blocked. Human identifies authority. |
| Unrelated worktree changes cannot be isolated | Do not commit. Block repair card. |
| Canonical verification or harness fails | Keep original blocked. Record output and next repair step. |
| Repair card active or workspace busy | Do not unblock original. Wait for repair completion or isolate worktree. |
