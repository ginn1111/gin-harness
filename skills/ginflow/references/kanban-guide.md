# Kanban guide

## Gate

Pre-card work may brainstorm, route, size, inspect read-only context, choose artifacts, and draft card content. Clarification remains read-only. Eligible XS/S Direct Work is the explicit exception: after every eligibility factor is affirmative, its Delivery Change may proceed without a card or Governance Artifact. Governed Work still requires one selected card before implementation investigation, code change, dispatch, progress, verification, completion, or handoff.

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

Draft card and artifact content before writing. Create the card assigned to the current profile, with its future links and `--initial-status blocked`. Write linked artifacts, then unblock once readiness passes. Current profile loads its canonical local Ginflow skill; do not force `--skill ginflow`.

For a malformed existing body, keep the task blocked and have the human edit title/body in the Kanban dashboard before rerunning the harness. `hermes kanban edit` is only for completed-task recovery fields, not body edits. Do not invent a CLI `--body` repair command or acceptance criteria. If dashboard repair is unavailable, replacing the card requires human approval and an explicit backlink/comment.

Before closing unfinished or blocked work, record outcome, changed files, verification, blockers, next step, and accurate status on card. Optional Markdown handoff export does not replace or mutate card.

Before completion, re-run canonical verification in target repo and derive changed-file evidence from target-repo `git status --short`. Temporary checks outside card workspace do not prove completion.

Before `kanban_complete`, worker prepares truthful verification evidence and exact linked target-local paths in `artifact_baseline`. Human review is not required for this baseline commit; never include unrelated work. The worker must commit every linked artifact and stage only exact linked artifacts plus intended card work. `ginflow-gate` validates card fields, verification metadata, baseline commit, exact paths, and drift during the tool call. Invalid or unavailable evidence rejects completion. Before startup, resume, handoff, or derived work involving that card, compare only those paths against commit. Unrelated paths and cards remain unblocked. Propose:

- restore the completed docs, create new versioned docs and a follow-up card, and link back to the completed card;
- reopen the card, reconcile docs with implementation and evidence, commit, record a new completion commit, rerun verification and the harness, and complete again; or
- after explicit human classification as editorial, commit the edit and advance the baseline with an approval note.

Never silently advance the completion commit or substitute per-file hashes.

Optional manual/CI candidate check:

```bash
python3 <setup-repo>/skills/ginflow/scripts/validate-harness.py \
  --setup-repo <setup-repo> --target <target-repo> \
  --kanban-task-id "$TASK_ID" --baseline-commit "$COMMIT" \
  --baseline-path docs/briefs/<CARD-ID>.md --json
```

Any worker assigned to card makes `kanban_complete` call with verification evidence plus same commit and paths in `metadata={"artifact_baseline": ...}`. Do not route completion through `gintary` or a review handoff. `ginflow-gate` revalidates synchronously before mutation and rejects invalid output. External harness rerun is optional manual/CI evidence.

Workspace rule:
- use real target repo
- `dir:/abs/path` for existing checkout
- `worktree` for isolated code changes

Do not leave project work in scratch workspace if files must be read from repo.

## Feedback boundary

Feedback v1 is a pure normalized contract for Governed Work lifecycle signals. It requires a stable `event_id` and Kanban `task_id`; Direct Work is excluded in v1 because it has no card identity. The builder does not persist events, notify, mutate Kanban, or infer work. Supported signals and next actions are defined in `CONTEXT.md`.

## Read-only background watcher

When an interactive agent starts a selected `running` card, launch one `/background` watcher pinned to that task ID and board. The watcher records its initial event boundary, reads/polls only that card, and never claims, edits, dispatches, blocks, completes, or mutates workspace/repository state. Suppress historical events, routine heartbeats, and unchanged status. Report only completed/terminal, blocked, failed, reclaimed/retried, or materially stalled transitions with evidence, then stop at terminal state. Do not start duplicate watchers. Non-interactive surfaces use an equivalent read-only process watcher or no watcher; they must not pretend to invoke `/background`.

Run target-declared project verification first. Run ginflow harness externally against target and selected card; never copy harness into target repo. Report project verification and harness result separately.
After setup-repo updates, use setup repo `scripts/verify.sh` only for profile drift.
