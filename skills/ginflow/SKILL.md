---
name: ginflow
description: Use for target-project startup, task shaping, execution, completion, Kanban handoff, project-doc layout, or setup-repo versus target-repo decisions under Hermes profiles.
---

# ginflow

Global workflow integration that Hermes-native profile distributions may load from setup repo.

## When to use

Use when any of these apply:
- starting work in blank project
- starting, executing, closing, or resuming target-project work
- deciding where docs belong
- deciding brief vs spec vs plan
- shaping Kanban task for selected execution profile
- exporting an optional session handoff from Kanban
- explaining setup-repo vs target-repo split

## Core split

- **Profile distribution** owns identity, manifest, native config defaults, and release/update lifecycle
- **Setup repo** owns optional shared skills, harness, MCP/plugin/tool wiring, and integration checks
- **Target repo** owns code, tests, local docs, local task artifacts
- **Task workspace** must point at real target repo

Never use setup repo as default code workspace.

## Doc layout

Put these in target repo when project needs them:

| Artifact | Purpose |
|---|---|
| `AGENTS.md` | local project rules, cross-agent portable |
| `.hermes.md` | Hermes-specific project rules |
| `docs/briefs/<CARD-ID>.md` | concrete task brief |
| `docs/specs/<CARD-ID>.md` | behavior/contract detail when needed |
| `docs/plans/<CARD-ID>.md` | execution order for medium+ work |
| `docs/handoffs/<CARD-ID>.md` | optional exported resume snapshot |
| `docs/adrs/` | durable architectural decisions |

`<CARD-ID>` is the stable human-facing work key chosen before card creation (for example `APP-9`) and used in the title and artifact paths. `$TASK_ID` is the Hermes-generated task ID (for example `t_ab12`) returned after creation and used by Kanban tools and `--kanban-task-id`. Do not rename artifacts to the generated ID; the harness follows explicit `Links:` paths.

Do not store artifacts in setup repo unless task explicitly changes global profile system.

Starter local context:
- copy `templates/AGENTS.md` from setup repo into target repo

## Task shaping

### Kanban boundary

Before a card exists, ginflow may brainstorm, inspect read-only context, choose work mode, size work, choose artifacts, and draft proposed card content. These actions shape work but do not start project execution.

After shaping, require one selected Kanban card before creating target artifacts, running implementation investigation, changing code, dispatching, recording progress, verifying completion, or handing off. No selected card blocks project execution.

Selected card must contain: ID, title, objective, scope, acceptance, workspace, status, assignee, and links. Missing required fields block execution until card is repaired.

### Choose work mode

1. **Investigation** — cause unclear
2. **Implementation** — requirement clear
3. **Brainstorming** — requirement unclear

### Choose artifact level

| Case | Brief | Spec | Plan |
|---|---:|---:|---:|
| XS/S clear work | yes | optional | optional |
| M work | yes | optional | yes |
| L/XL or risky work | yes | yes | yes |
| Investigation | yes | optional | yes |
| Brainstorming | note first | later | later |

Rule:
- brief always
- spec when behavior/contract can drift
- plan when ordering/risk matters
- Before creating a plan for planning-required work, load and follow the `plan` skill.
- use Kanban card ID across artifacts for deterministic linking
- brief defines objective/scope/acceptance; spec defines behavior/contracts; plan defines execution order
- follow `references/artifact-content-guide.md` for content quality, artifact boundaries, authority, ADRs, cards, and handoffs

## Project session startup

Before target-project work:

1. Confirm workspace points at real target repo.
2. Read local `AGENTS.md` / `.hermes.md`.
3. **Check Kanban board state:**
   - If no Kanban cards exist → route to work shaping/sizing (investigation/brainstorming/implementation choice, artifact level, draft card).
   - If Kanban cards exist → read progress first (use `kanban_list`/`kanban_show` TOOLS in agent code), then resume from selected/active card.
4. Require and read selected or assigned Kanban card. Stop if absent.
5. Confirm all required card fields and workspace. Stop if incomplete.
6. Read linked brief/spec/plan when present.
7. If the selected card is completed, run the linked-artifact drift gate before any project action.
8. Inspect git state and run project baseline verification.
9. Run external ginflow harness against target repo and selected card; do not copy harness into target repo.
10. Report project verification and ginflow harness separately.
11. Route execution as investigation or implementation. Brainstorming may occur before card selection.

Stop when any required input is missing and risk is material.

## Tool-vs-CLI boundary

**Complete cards with the `kanban_complete` TOOL — never the `hermes kanban complete` CLI.**

The `ginflow-gate` plugin hooks only fire on the native `kanban_complete` tool call. The CLI bypasses both:

- `pre_tool_call` — blocks malformed completions (missing fields, mismatched verification/artifact commits, linked-artifact drift). Without it, bad completions sail through.
- `post_tool_call` — appends `**Status: completed** — linked card <CARD-ID> is done.` to each linked brief/spec/plan file. Without it, artifacts stay stale/active.

Board reads (`kanban_list`, `kanban_show`) should also use the TOOLS, not the `hermes kanban` CLI, so progress flows through the same governed path.

**Syntax:**
```
kanban_complete(task_id='<card-id>', result='<short result>',
  metadata={'verification_result': {'commit': '<commit>', 'command': 'make test', 'result': 'passed'},
            'artifact_baseline': {'commit': '<commit>', 'paths': ['docs/briefs/<card-id>.md']}})
```

- ✅ `kanban_complete(task_id='t_abc123', result='Build finished', metadata={...})`
- ❌ `hermes kanban complete t_abc123 --result 'Build finished' --metadata {...}`

If you are about to run `hermes kanban complete ...` in a terminal, stop and call the `kanban_complete` tool instead.

## Execution contract

- One active card per mutable workspace. Parallel cards are allowed only when each uses an isolated worktree or a different workspace. Hermes dispatcher claim remains the mechanical authority; no public `kanban_claim` tool exists for plugin interception, so atomic workspace-collision enforcement requires Hermes core.
- No target-project execution without selected, complete card.
- Do not resume, hand off, or derive work from a completed card while its linked-artifact drift is unresolved. Unrelated cards and unlinked project work may continue.
- Stay inside card scope and target workspace.
- Use project-native commands and local conventions.
- Block on material ambiguity; do not invent requirements.
- Preserve real verification evidence.

## Definition of done

Work is done only when:

- [ ] Acceptance criteria are satisfied.
- [ ] Relevant project checks ran and passed.
- [ ] Changed files were reviewed against scope.
- [ ] Verification evidence is recorded on Kanban card.
- [ ] Kanban status is accurate.
- [ ] Linked artifacts (brief/spec/plan) reflect completion — mark as done, superseded, or final; do not leave them in active/progress state.
- [ ] Repo is restartable from documented verification path.
- [ ] Remaining limits or blockers are explicit.

## Kanban card shape

Keep card thin.

Include only:
- objective
- scope
- acceptance criteria
- link to project artifact if present

At completion, also store a path-scoped `artifact_baseline` with the Git completion commit and exact target-local linked artifact paths. This is verification metadata, not duplicated artifact content.

For a live Hermes Kanban card, use these exact body labels. `ginflow-gate` rejects malformed completion attempts:

```text
Objective: <what to achieve>
Scope:
- <files/dirs/areas>
Acceptance:
- <observable completion check>
Links:
- docs/briefs/<CARD-ID>.md
```

Hermes stores workspace, status, assignee, and ID on the task row. It stores `artifact_baseline` in the latest completion run metadata. The harness reads both locations; do not create a second shadow card JSON format.

To avoid dispatch racing ahead of linked artifacts, draft card and artifact contents in memory, then create card assigned to the current profile, with complete future `Links:` paths and `--initial-status blocked`. Write and commit linked target artifacts, then run project checks and external candidate-baseline harness. Unblock only after dispatch readiness passes. Current profile loads its configured Ginflow skill; do not force `--skill ginflow`.

If an existing live body is missing required sections, keep it blocked and ask the human to edit the title/body in the Kanban dashboard, then rerun the harness. The current CLI `hermes kanban edit` only backfills completed-task result/summary/metadata; do not invent a `--body` option. If dashboard repair is unavailable, create a corrected replacement card only with human approval and preserve a link/comment back to the malformed card.

Use real target repo workspace:
- `--workspace dir:/abs/path/to/project`
- `--workspace worktree` for isolated git changes

## Required fields for build-ready handoff

A task for current profile should answer:
- what to change
- where to change it
- how done is judged
- what not to touch

If any missing and risk is material, keep card blocked and ask Gin.

## Session close and restart

Kanban card is default durable handoff. Before ending unfinished or blocked work, record on card:

- outcome and completed work
- changed files
- verification commands and results
- blockers or risks
- exact next step
- accurate status

Next session resumes from selected card, linked artifacts, local rules, and repository state. Session transcript and memory are supporting context, not source of truth.

## Completion report

**Complete the card with the `kanban_complete` TOOL — never the `hermes kanban complete` CLI.** The `ginflow-gate` plugin's `post_tool_call` hook only fires on the native `kanban_complete` tool call; completing via the CLI bypasses the hook that auto-marks linked artifacts done and the blocking validation gate. Always route completion through the tool, not a shell command.

Immediately before reporting completion:

1. Run canonical project verification declared by target repo.
2. Read target-repo `git status --short`; use `git diff --stat` when useful.
3. Run ginflow harness externally against target repo and selected card. Never copy harness script into target repo.
4. Report project verification and ginflow harness as separate results.
5. Report only files under selected card workspace.
6. Quote canonical project command and exact fresh result.
7. Record same evidence on selected Kanban card before completing it.
8. `ginflow-gate` synchronously validates required card fields, verification evidence, completion commit, exact linked paths, and drift before `kanban_complete`; validation errors fail closed with an actionable rejection. Record `metadata.verification_result` (`commit`, `command`, `result`) and matching `metadata.artifact_baseline` (`commit`, `paths`) in the completion call.
9. The external CLI harness remains available for manual and CI validation independent of the live plugin gate.
10. Review target workspace using `references/workspace-health-warnings.md`. Record concise findings under `Workspace warnings` on card and in completion report. Warnings do not block by default; promote only when acceptance, canonical verification, security, privacy, data integrity, or restartability is affected. Do not copy warning policy or scanner files into target repo.

Project verification proves product behavior and blocks completion when it fails. Ginflow harness proves workflow readiness and drift: report failures as warnings, but treat missing card, wrong workspace, missing acceptance, missing required artifact, missing completion verification path, missing completed-card artifact baseline, or changed completed-card linked artifact as blockers for the affected lifecycle stage. Harness unavailable is a warning and never substitutes for project verification.

Temporary or ad-hoc checks are not completion evidence unless selected card explicitly targets that temporary artifact. Do not create or report unrelated temporary checks when canonical project verification exists. If canonical verification is unavailable or fails, report blocked/not done.

Live harness examples:

```bash
# Startup/resume: reads the task row, body, and latest run metadata directly.
python3 <setup-repo>/skills/ginflow/scripts/validate-harness.py \
  --setup-repo <setup-repo> --target <target-repo> \
  --kanban-task-id "$TASK_ID" --json

# Pre-completion: validates the exact baseline that will be sent to kanban_complete.
python3 <setup-repo>/skills/ginflow/scripts/validate-harness.py \
  --setup-repo <setup-repo> --target <target-repo> \
  --kanban-task-id "$TASK_ID" --baseline-commit "$COMMIT" \
  --baseline-path docs/briefs/<CARD-ID>.md --json
```

The live harness reads from the current board. `--card <json-file>` remains available for fixtures and accepts either normalized Ginflow JSON or saved `hermes kanban show --json` output.

## Harness subsystem mapping

| Subsystem | Ginflow implementation |
|---|---|
| Instructions | profile distribution chooses whether to route to `ginflow`; target `AGENTS.md` stores local context |
| State | Hermes Kanban card and linked artifacts |
| Verification | project-native canonical command and card evidence |
| Scope | card objective, scope, acceptance, workspace, and one active card per mutable workspace |
| Lifecycle | startup, close, restart, and optional Markdown export in `ginflow` |

`feature_list.json`, `progress.md`, `init.sh`, and mandatory handoff files are not required equivalents.

## Optional session handoff export

Use `/hermes handoff export` only when Gin wants a portable Markdown snapshot. Export never replaces Kanban.

Flow:

1. Ask Gin which Kanban card to export. Never auto-select.
2. Read selected card and only cards explicitly linked from it. Do not recurse.
3. Read brief/spec/plan links recorded on selected card.
4. In target repo, read `git config user.name` and `git config user.email`.
5. Render `templates/session-handoff.md` preview.
6. Use `Not recorded on Kanban card.` for missing card data and `Not linked from selected Kanban card.` for missing artifact links. Use `Not configured in Git.` for missing Git identity.
7. Ask Gin to approve content and output path. Default: `docs/handoffs/<CARD-ID>.md`; local project convention wins.
8. Write only after approval.

Never infer missing facts from status, chat, OS identity, commit history, or unrelated cards. Never mutate card status, assignee, links, or content during export.

## Drift detection

Use drift detection in 2 layers, in this order:

1. **Project verification first** — target repo declares its own canonical command
   - examples: `./verify.sh`, `make verify`, or project-native command
   - proves project behavior; ginflow does not force script location
2. **Global setup drift second** — setup repo `scripts/verify.sh`
   - checks requested profiles retain native identity while setup integrations are present
   - checks skill/plugin links, MCP/tool wiring, and shared harness health

Rule:
- target repo drift check comes first during real work
- setup repo `verify.sh` is only for profile installation health
- do not mix them
- ginflow harness remains in setup/deployed skill and runs externally against target repo; never copy it into target repo

### Completed-card artifact gate

- Before completion, worker must commit every target-local linked artifact. Worker may create this baseline commit without human review; stage only exact linked artifacts plus card-scoped implementation files, use the target repository's configured Git identity, then store `artifact_baseline.commit` and `artifact_baseline.paths`. Paths must exactly match the card's linked local docs. If Git identity is absent, commit fails, or unrelated changes cannot be excluded, block completion and request human help.
- On startup, resume, handoff, or derived work involving that completed card, compare only those paths against the completion commit. Do not compare the whole repository.
- A missing/unavailable commit, path-list mismatch, missing artifact, committed change, or uncommitted change is suspected drift and blocks use of that card as authority. Unrelated paths and unrelated cards remain unblocked.
- The harness cannot reliably identify the editor or determine materiality, so a human chooses one resolution.
- Resolution A — new intent: restore the completed artifact, create new versioned docs and a follow-up card, and link both back to the completed card.
- Resolution B — changed completed scope: reopen the card, reconcile artifacts with implementation, acceptance, and verification evidence, commit the result, record the new completion commit, rerun verification and the harness, then complete again.
- Resolution C — editorial only: after explicit human classification, commit the editorial change, advance the baseline commit, and record an approval note without reopening implementation work.
- Never silently advance a completion commit. Do not use per-file SHA fallback.

## Blank project flow

If user starts in blank project:

1. inspect repo for `AGENTS.md` / `.hermes.md`
2. if missing and setup template is available, copy setup repo `templates/AGENTS.md` before project-specific edits
3. add build/test/lint/run commands if known
4. add forbidden areas / deploy rules if known
5. if commands are unknown, leave placeholders and mark them missing
6. retain routing line that sends shared workflow to `ginflow`
7. document one canonical verification command; `verify.sh`, `make verify`, or a project-native command are valid
8. if repo has executable project files, run baseline verification; otherwise record `baseline unavailable: no implementation yet`
9. only then shape first task

Minimum local setup:
- `AGENTS.md` or `.hermes.md`
- install/dev/build/test/lint commands
- key directories
- forbidden/sensitive paths
- definition of done / verification path
- drift-detection contract: local authorities, generated-file relationships, and remediation order
- project summary and commands
- file/git conventions and project-specific completion additions

Blank-project workspace pitfall:
- if `PWD` says target repo but tools act in another repo, check `TERMINAL_CWD`
- stale `TERMINAL_CWD` can override real project cwd
- for clean target-repo tests, unset it: `env -u TERMINAL_CWD hermes ...`

## Stop rules

Stop and clarify when:
- wrong repo
- no selected Kanban card after pre-card shaping
- selected card missing required fields
- completed card missing a valid path-scoped completion commit for linked local docs
- completed card linked artifact missing, committed after, or uncommitted relative to its completion commit
- fuzzy requirement
- unclear cause but user expects direct fix
- acceptance criteria missing
- no verification path
- **about to complete a card with the `hermes kanban complete` CLI instead of the `kanban_complete` tool**

## References

- `references/artifact-content-guide.md`
- `references/doc-layout.md`
- `references/kanban-guide.md`
- `references/drift-detect.md`
- `references/blank-project-checklist.md`
- `references/workspace-health-warnings.md`
- `templates/brief.md`
- `templates/plan.md`
- `templates/spec.md`
- `templates/kanban-task.md`
- `templates/session-handoff.md`
- setup repo `templates/AGENTS.md`
