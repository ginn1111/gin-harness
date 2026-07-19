# Kanban guide

## Gate

Pre-card work may brainstorm, route, size, inspect read-only context, choose artifacts, and draft card content. Any target artifact creation, implementation investigation, code change, dispatch, progress, verification, completion, or handoff requires one selected card.

No selected card blocks execution. Selected card requires ID, title, objective, scope, acceptance, workspace, status, assignee, and links. Missing field blocks execution until repaired.

Thin card pattern:
- title
- 1-2 sentence objective
- scope
- acceptance
- link to artifact if present

Use these exact body labels on Hermes Kanban cards; the external harness parses them from `hermes kanban show --json`:

```text
Objective: <what to achieve>
Scope:
- <files/dirs/areas>
Acceptance:
- <observable completion check>
Links:
- docs/briefs/<CARD-ID>.md
```

Pass workspace and assignee through Kanban task fields, not duplicate body prose. The harness maps `workspace_kind` + `workspace_path`, status, assignee, and ID from the task row. On completed cards it reads `artifact_baseline` from the latest run metadata.

Use a stable human-facing card key chosen before creation for linked artifacts; use the separate Hermes-generated task ID (`t_...`) for Kanban commands:
- `docs/briefs/<CARD-ID>.md`
- `docs/specs/<CARD-ID>.md`
- `docs/plans/<CARD-ID>.md`

Put the key in the task title and explicit `Links:` paths. The harness follows those links rather than deriving filenames from the generated task ID.

Draft card and artifact content before writing. Create the card without an assignee, with its future links and `--initial-status blocked`. Do not emit a setup `needs_input` block; reserve the first explicit block for `ginb`'s review handoff so recurrence protection does not move the card to triage. Write and commit linked artifacts, assign `ginb`, validate the candidate baseline, then unblock once. The assigned `ginb` profile loads its canonical local Ginflow skill; do not force `--skill ginflow` because the claiming dispatcher profile resolves task skills and another gateway may not expose that name.

For a malformed existing body, keep the task blocked and have the human edit title/body in the Kanban dashboard before rerunning the harness. `hermes kanban edit` is only for completed-task recovery fields, not body edits. Do not invent a CLI `--body` repair command or acceptance criteria. If dashboard repair is unavailable, replacing the card requires human approval and an explicit backlink/comment.

Before closing unfinished or blocked work, record outcome, changed files, verification, blockers, next step, and accurate status on card. Optional Markdown handoff export does not replace or mutate card.

Before completion, re-run canonical verification in target repo and derive changed-file evidence from target-repo `git status --short`. Temporary checks outside card workspace do not prove completion.

Commit every target-local artifact linked from a card, then record the Git completion commit and exact linked paths under card `artifact_baseline`. If the worker lacks commit permission, keep the card open and ask the human to commit; never create one implicitly. Before startup, resume, handoff, or derived work involving that card, compare only those paths against the commit. A missing/unavailable commit, path mismatch, missing file, later commit, or uncommitted edit blocks use of that card as authority. Unrelated paths and cards remain unblocked. Propose:

- restore the completed docs, create new versioned docs and a follow-up card, and link back to the completed card;
- reopen the card, reconcile docs with implementation and evidence, commit, record a new completion commit, rerun verification and the harness, and complete again; or
- after explicit human classification as editorial, commit the edit and advance the baseline with an approval note.

Never silently advance the completion commit or substitute per-file hashes.

Before handoff to `gintary`, `ginb` validates the candidate baseline against the live card:

```bash
python3 <setup-repo>/skills/ginflow/scripts/validate-harness.py \
  --setup-repo <setup-repo> --target <target-repo> \
  --kanban-task-id "$TASK_ID" --baseline-commit "$COMMIT" \
  --baseline-path docs/briefs/<CARD-ID>.md --json
```

`ginb` comments verification evidence plus the exact payload, then blocks with `review-required: Ginflow completion baseline ready`; it does not call `kanban_complete` for tasks with target-local artifact links. `gintary` revalidates and makes the first and only completion call with the same commit and paths in `metadata={"artifact_baseline": ...}`. Then rerun with only `--kanban-task-id` to verify persisted metadata. Add harness `--board <slug>` for a non-current board.

Workspace rule:
- use real target repo
- `dir:/abs/path` for existing checkout
- `worktree` for isolated code changes

Do not leave project work in scratch workspace if files must be read from repo.

Run target-declared project verification first. Run ginflow harness externally against target and selected card; never copy harness into target repo. Report project verification and harness result separately.
After setup-repo updates, use setup repo `scripts/verify.sh` only for profile drift.
