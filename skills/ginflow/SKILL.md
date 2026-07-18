---
name: ginflow
description: Use for target-project startup, task shaping, execution, completion, Kanban handoff, project-doc layout, or setup-repo versus target-repo decisions under gin Hermes profiles.
---

# ginflow

Global workflow guide shared by installed profiles from setup repo.

## When to use

Use when any of these apply:
- starting work in blank project
- starting, executing, closing, or resuming target-project work
- deciding where docs belong
- deciding brief vs spec vs plan
- shaping Kanban task for `ginb`
- exporting an optional session handoff from Kanban
- explaining setup-repo vs target-repo split

## Core split

- **Setup repo** owns global profiles, shared skills, setup/update scripts
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
- use Kanban card ID across artifacts for deterministic linking
- brief defines objective/scope/acceptance; spec defines behavior/contracts; plan defines execution order
- follow `references/artifact-content-guide.md` for content quality, artifact boundaries, authority, ADRs, cards, and handoffs

## Project session startup

Before target-project work:

1. Confirm workspace points at real target repo.
2. Read local `AGENTS.md` / `.hermes.md`.
3. Require and read selected or assigned Kanban card. Stop if absent.
4. Confirm all required card fields and workspace. Stop if incomplete.
5. Read linked brief/spec/plan when present.
6. Inspect git state and run project baseline verification.
7. Run external ginflow harness against target repo and selected card; do not copy harness into target repo.
8. Report project verification and ginflow harness separately.
9. Route execution as investigation or implementation. Brainstorming may occur before card selection.

Stop when any required input is missing and risk is material.

## Execution contract

- One active card per worker.
- No target-project execution without selected, complete card.
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
- [ ] Repo is restartable from documented verification path.
- [ ] Remaining limits or blockers are explicit.

## Kanban card shape

Keep card thin.

Include only:
- objective
- scope
- acceptance criteria
- link to project artifact if present

Use real target repo workspace:
- `--workspace dir:/abs/path/to/project`
- `--workspace worktree` for isolated git changes

## Required fields for build-ready handoff

A task for `ginb` should answer:
- what to change
- where to change it
- how done is judged
- what not to touch

If any missing and risk is material, block back to `gintary`.

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

Immediately before reporting completion:

1. Run canonical project verification declared by target repo.
2. Read target-repo `git status --short`; use `git diff --stat` when useful.
3. Run ginflow harness externally against target repo and selected card. Never copy harness script into target repo.
4. Report project verification and ginflow harness as separate results.
5. Report only files under selected card workspace.
6. Quote canonical project command and exact fresh result.
7. Record same evidence on selected Kanban card before completing it.

Project verification proves product behavior and blocks completion when it fails. Ginflow harness proves workflow readiness and drift: report failures as warnings, but treat missing card, wrong workspace, missing acceptance, missing required artifact, or missing completion verification path as blockers for affected lifecycle stage. Harness unavailable is a warning and never substitutes for project verification.

Temporary or ad-hoc checks are not completion evidence unless selected card explicitly targets that temporary artifact. Do not create or report unrelated temporary checks when canonical project verification exists. If canonical verification is unavailable or fails, report blocked/not done.

## Harness subsystem mapping

| Subsystem | Ginflow implementation |
|---|---|
| Instructions | profiles route to `ginflow`; target `AGENTS.md` stores local context |
| State | Hermes Kanban card and linked artifacts |
| Verification | project-native canonical command and card evidence |
| Scope | card objective, scope, acceptance, workspace, and one active card |
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
   - checks deployed profiles still match setup repo
   - checks symlinks, config paths, shared skills, bundled-skill opt-out

Rule:
- target repo drift check comes first during real work
- setup repo `verify.sh` is only for profile installation health
- do not mix them
- ginflow harness remains in setup/deployed skill and runs externally against target repo; never copy it into target repo

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
- fuzzy requirement
- unclear cause but user expects direct fix
- acceptance criteria missing
- no verification path

## References

- `references/artifact-content-guide.md`
- `references/doc-layout.md`
- `references/kanban-guide.md`
- `references/drift-detect.md`
- `references/blank-project-checklist.md`
- `templates/brief.md`
- `templates/plan.md`
- `templates/spec.md`
- `templates/kanban-task.md`
- `templates/session-handoff.md`
- setup repo `templates/AGENTS.md`
