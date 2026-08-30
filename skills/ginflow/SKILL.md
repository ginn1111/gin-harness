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
- deciding whether a Spec or Plan is needed
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

| Artifact     | Purpose                                   |
| ------------ | ----------------------------------------- |
| `AGENTS.md`  | local project rules, cross-agent portable |
| `.hermes.md` | Hermes-specific project rules             |

| `docs/specs/<CARD-ID>.md` | behavior/contract detail when needed |
| `docs/plans/<CARD-ID>.md` | execution order for medium+ work |
| `docs/handoffs/<CARD-ID>.md` | optional exported resume snapshot |
| `docs/adrs/` | durable architectural decisions |

`<CARD-ID>` is the stable human-facing work key chosen before card creation (for example `APP-9`) and used in the title and artifact paths. `$TASK_ID` is the Hermes-generated task ID (for example `t_ab12`) returned after creation and used by Kanban tools and `--kanban-task-id`. Do not rename artifacts to the generated ID; the harness follows explicit `Links:` paths.

Do not store artifacts in setup repo unless task explicitly changes global profile system.

Starter local context:

- copy `templates/AGENTS.md` from setup repo into target repo

## Task shaping

### Kanban status mapping

Ginflow uses logical states; Hermes Kanban stores the physical states. Routing must map before decision:

| Ginflow logical state | Hermes Kanban state |
| --------------------- | ------------------- |
| `next`                | `todo` or `ready`   |
| `in_progress`         | `running`           |
| `blocked`             | `blocked`           |
| `done`                | `done`              |
| `cancelled`           | `archived`          |

Never write `in_progress` to Hermes Kanban. `running` is active work. `todo`/`ready` requires startup validation before claim.

### Kanban boundary

Before a card exists, ginflow may brainstorm, inspect read-only context, choose work mode, size work, choose artifacts, and draft proposed card content. Clarification remains conversation-only and read-only. Direct Work is the explicit exception: after every eligibility factor is affirmatively established, eligible XS/S implementation may proceed without a card or Governance Artifact.

Governed Work requires one selected Kanban card before creating governed artifacts, running implementation investigation, changing code, dispatching, recording progress, verifying completion, or handing off. No selected card blocks project execution for Governed Work. Direct Work must remain inside its affirmatively established scope and must stop and re-route if scope, risk, ownership, clarity, or verification changes.

Selected card must contain: ID, title, objective, scope, acceptance, workspace, status, assignee, and links. Missing required fields block Governed Work until the card is repaired.

### Choose artifact level

| Case                                     | Kanban card |        Spec |        Plan |
| ---------------------------------------- | ----------: | ----------: | ----------: |
| Direct Work — eligible XS/S              |          no |          no |          no |
| Governed Work — M                        |    required | conditional | conditional |
| Governed Work — L/XL or risky            |    required | conditional | conditional |
| Clarification or read-only investigation |          no |          no |          no |

Rule:

- Direct Work creates no Kanban card or Governance Artifact.
- Governed Work requires a card; choose Spec when behavior or contract can drift and Plan when ordering, investigation, rollback, coordination, or layered verification matters.

- Before creating a plan for planning-required work, load and follow the `plan` skill.
- Use the Kanban card ID across governed artifacts for deterministic linking.
- Follow linked artifact templates and project-local rules for content quality and boundaries.
- All Ginflow Markdown artifacts use YAML frontmatter at byte 0 for metadata. Specs and plans use `status`, `size`, `scope`, and `owner`; keep lifecycle state in the header and do not duplicate it as body-only `Status:` metadata.

### Routing guidance and feedback boundary

When no selected/running card owns the workspace, use the injected routing guidance to evaluate Work Mode, Work Size, Risk Impact, and Direct Work Eligibility. The three outcomes are:

- affirmative XS/S eligibility → Direct Work (`direct-no-card`), with Delivery Change plus conversation result only;
- known M/L/XL size, actual Risk Impact, or Governance Artifact need → Governed Work with a build-ready card and conditional Spec/Plan outputs;
- any unresolved requirement or routing fact → Clarification with read-only investigation only and no mutation.

Direct Work Eligibility is affirmative evidence for clarity, known cause, genuine XS/S size, localized reversible scope, no actual Risk Impact, no Governance Artifact need, known canonical verification, project-local permission, and an unowned single-worker workspace. Raw file count, title wording, and risky keywords are not sufficient evidence. Stop mutation and reclassify if scope, clarity, ownership, verification, or impact changes.

The plugin's candidate skill mapping is deterministic guidance, not semantic similarity search or authorization. Hermes must call `skill_view(name='...')`; the plugin never calls it, inspects skill contents, creates cards/artifacts, or mutates Kanban. Canonical output precedence is target-project rules, explicit route/card contract, Ginflow matrix, selected skill, then skill defaults. Adapt skill output into the selected canonical artifact rather than duplicating it.

Feedback v1 is a pure Governed Work lifecycle event contract. It validates stable event/task identifiers, supported signals, single-line safe fields, and RFC3339 UTC timestamps, then returns a fresh dictionary. It does not persist, notify, mutate Kanban, or infer work. Direct Work has no feedback event in v1. Supported signal mappings are documented in `CONTEXT.md`.

## Project session startup

### Canonical project context

On the first `/ginflow` load in a project, inspect `.ginflow.yaml` at the current repository root. Do not create a `ginflow` CLI and do not read, migrate, or write `.hermes/ginflow.yaml` or Hermes global config. If the project-local file is absent, show the resolved workspace and current/default Kanban board, then ask whether to use that board or create a new one. A new board requires a non-empty user-provided board name; create it through native Kanban operations before writing the config.

```yaml
version: 1
ginflow:
  board: <Kanban board slug>
  workspace: /absolute/path/to/project
  worker:
    profile: <worker Hermes profile>
    provider: <provider name>
    model: <model name>
  trace: false # optional; enables ginflow-trace function logging
```

`workspace` is the resolved project directory and `board` is the selected board. Resolution precedence is explicit command/API override, `HERMES_KANBAN_BOARD`, the existing `.ginflow.yaml`, then Hermes's active board. The optional `worker` block stores repository-local dispatch defaults: `profile` maps to `kanban_create.assignee`, and `provider`/`model` are passed as explicit `kanban_create` overrides when present. Only board and workspace are required; the worker block is recommended for reproducible dispatch and never invalidates a minimal config.

Before creating a governed card, `/ginflow` checks the configured worker block. When any of `profile`, `provider`, or `model` is absent, it shows the resolved fallback and asks whether to enter the complete block first; entered values are validated and atomically merged into the existing `.ginflow.yaml` before card creation, preserving board, workspace, version, and unrelated keys. Skipped setup leaves the config unchanged and falls back to the current Hermes profile for `assignee`, omitting provider/model so the selected profile's own defaults apply. The prompt repeats at the next card creation until defaults are configured. Explicit per-card user overrides win over repository defaults without rewriting the config. A malformed worker block (wrong type, empty string, or unknown field) blocks card creation without breaking read-only board/workspace routing. A missing config must be initialized by `/ginflow` before governed Kanban work. First-load initialization is agent-procedural: runtime validation and persistence enforce the contract, but no runtime hook or CLI silently initializes a project. A malformed, incomplete, or workspace-mismatched config fails closed; do not overwrite it or silently switch workspace/board. Existing valid config is not rewritten during ordinary skill loading, and project verification only reads it. Gate routing distinguishes missing config (run `/ginflow` to initialize) from invalid config (repair `.ginflow.yaml`); a valid config with no workspace cards remains a normal no-card work-shaping route.

`ginflow.trace` is optional and defaults off. See `references/project-context.md` for the enablement contract (env override, log locations).

Before target-project work, determine whether the request is Direct Work, Governed Work, or Clarification. The card and Kanban checks below apply to Governed Work; Direct Work still requires affirmative eligibility, project-local permission, and known canonical verification.

1. Confirm workspace points at real target repo.
2. Read local `AGENTS.md` / `.hermes.md`.
3. **Check Kanban board state:**
   - If no Kanban cards exist → route to work shaping/sizing (investigation/brainstorming/implementation choice, artifact level, draft card).
   - If Kanban cards exist → read progress first (use `kanban_list`/`kanban_show` TOOLS in agent code), then resume from selected/active card.
4. For Governed Work, require and read the selected or assigned Kanban card. Stop if absent.
5. For Governed Work, confirm all required card fields and workspace. Stop if incomplete.
6. Read linked spec/plan when present.
7. If the selected card is completed, run the linked-artifact drift gate before any project action.
8. Inspect git state and run project baseline verification.
9. For Governed Work, run external ginflow harness against target repo and selected card; do not copy harness into target repo.
10. Report project verification and Ginflow harness separately when Governed Work applies.
11. Follow routing context injected by `ginflow-gate`; it chooses work mode only when no card exists.

### Kanban task notifications

Do not launch a `/background` watcher for the selected running card. Kanban task creation from a persistent TUI or gateway session auto-subscribes the originating session when `kanban.auto_subscribe_on_create` is enabled; treat `subscribed: true` in the creation result as confirmation. Terminal events are delivered by the dispatcher, and the subscription is removed after the task reaches `done` or `archived`. If creation does not confirm a subscription, use the normal Kanban notification subscription surface or explicit board reads instead of hidden polling.

Stop when any required input is missing and risk is material.

## Kanban completion validation

The `ginflow-gate` completion policy is integrated with the native `kanban_complete` tool call:

- `pre_tool_call` blocks malformed completions, linked local spec/plan documents that are not marked completed, mismatched verification/artifact commits, and linked-artifact drift.
- The blocking message lists incomplete linked documents and tells the agent to finalize and commit them before retrying. Documents are never mutated after the card is done.

**Syntax:**

```
kanban_complete(task_id='<card-id>', result='<short result>',
  metadata={'verification_result': {'commit': '<commit>', 'command': 'make test', 'result': 'passed'},
            'artifact_baseline': {'commit': '<commit>', 'paths': ['docs/specs/<card-id>.md']}})
```

- `kanban_complete(task_id='t_abc123', result='Build finished', metadata={...})`

## Execution contract

- One active card per mutable workspace. Parallel cards are allowed only when each uses an isolated worktree or a different workspace. Hermes dispatcher claim remains the mechanical authority; no public `kanban_claim` tool exists for plugin interception, so atomic workspace-collision enforcement requires Hermes core.
- No Governed Work execution without a selected, complete card. Direct Work is allowed only after affirmative eligibility and creates no card or Governance Artifact.
- Do not resume, hand off, or derive work from a completed card while its linked-artifact drift is unresolved. Unrelated cards and unlinked project work may continue.
- Stay inside card scope and target workspace for Governed Work; keep Direct Work inside its explicitly established scope and workspace.
- Use project-native commands and local conventions.
- Block on material ambiguity; do not invent requirements.
- Preserve real verification evidence.

## Definition of done

Work is done only when:

- [ ] Acceptance criteria are satisfied.
- [ ] Relevant project checks ran and passed.
- [ ] Changed files were reviewed against scope.
- [ ] Governed Work records verification evidence on its Kanban card, or Direct Work reports exact evidence in its scoped result.
- [ ] Governed Work Kanban status is accurate.
- [ ] Governed Work linked artifacts reflect completion — mark them done, superseded, or final; do not leave them in active/progress state.
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
- docs/specs/<CARD-ID>.md
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

Use the native `kanban_complete` tool when completion must pass through `ginflow-gate`; the external CLI harness remains available for manual and CI validation.

Immediately before reporting completion:

1. Run canonical project verification declared by target repo.
2. Read target-repo `git status --short`; use `git diff --stat` when useful.
3. Report only files under selected card workspace.
4. Quote canonical project command and exact fresh result.
5. Record same evidence on selected Kanban card before completing it.
6. Finalize every linked local spec/plan with YAML frontmatter at byte 0 declaring `status: completed`, commit those document changes, update matching verification and artifact-baseline commits, then call `kanban_complete` directly. Body status text is ignored. Any worker may complete its assigned card; do not route completion to `gintary` or a review handoff.
7. Provide `metadata.verification_result` (`commit`, `command`, `result`) and matching `metadata.artifact_baseline` (`commit`, `paths`). `ginflow-gate` validates these synchronously, including exact linked paths and drift, and rejects invalid completion.
8. The external CLI harness remains available for manual and CI validation independent of the live plugin gate.
9. Review target workspace using `references/workspace-health-warnings.md`. Record concise findings under `Workspace warnings` on card and in completion report. Warnings do not block by default; promote only when acceptance, canonical verification, security, privacy, data integrity, or restartability is affected. Do not copy warning policy or scanner files into target repo.

Project verification proves product behavior and should be reported truthfully. `ginflow-gate` is completion authority: it validates card fields, verification metadata, linked artifact baseline, and drift synchronously, then rejects invalid `kanban_complete` calls. External harness remains optional manual/CI evidence and never substitutes for project verification.

Temporary or ad-hoc checks are not completion evidence unless selected card explicitly targets that temporary artifact. Do not create or report unrelated temporary checks when canonical project verification exists. If canonical verification is unavailable or fails, report blocked/not done.

Live harness examples:

```bash
# Startup/resume: reads the task row, body, and latest run metadata directly.
python3 <setup-repo>/skills/ginflow/scripts/validate-harness.py \
  --setup-repo <setup-repo> --target <target-repo> \
  --kanban-task-id "$TASK_ID" --json

# Optional CI/manual candidate check before kanban_complete.
# ginflow-gate performs authoritative validation during the tool call.
python3 <setup-repo>/skills/ginflow/scripts/validate-harness.py \
  --setup-repo <setup-repo> --target <target-repo> \
  --kanban-task-id "$TASK_ID" --baseline-commit "$COMMIT" \
  --baseline-path docs/specs/<CARD-ID>.md --json
```

The live harness reads from the current board. `--card <json-file>` remains available for fixtures and accepts either normalized Ginflow JSON or saved `hermes kanban show --json` output. It is optional evidence; workers do not need a separate harness handoff before calling `kanban_complete`.

## Harness subsystem mapping

| Subsystem    | Ginflow implementation                                                                              |
| ------------ | --------------------------------------------------------------------------------------------------- |
| Instructions | profile distribution chooses whether to route to `ginflow`; target `AGENTS.md` stores local context |
| State        | Hermes Kanban card and linked artifacts                                                             |
| Verification | project-native canonical command and card evidence                                                  |
| Scope        | card objective, scope, acceptance, workspace, and one active card per mutable workspace             |
| Lifecycle    | startup, close, restart, and optional Markdown export in `ginflow`                                  |

`feature_list.json`, `progress.md`, `init.sh`, and mandatory handoff files are not required equivalents.

## Optional session handoff export

Use `/hermes handoff export` only when Gin wants a portable Markdown snapshot. Export never replaces Kanban.

Flow:

1. Ask Gin which Kanban card to export. Never auto-select.
2. Read selected card and only cards explicitly linked from it. Do not recurse.
3. Read spec/plan links recorded on selected card.
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

- The worker must commit every linked artifact and prepare truthful `artifact_baseline.commit` and exact target-local linked `artifact_baseline.paths` when calling `kanban_complete`. Worker may create this baseline commit without human review; stage only exact linked artifacts and intended card-scoped implementation files.
- Never copy harness script into target repo. Report project verification and ginflow harness as separate results.
- `ginflow-gate` is enforcement authority. During `kanban_complete`, it synchronously validates required card fields, verification metadata, baseline commit, exact linked paths, and artifact drift. Invalid or unavailable evidence rejects completion.
- On startup, resume, handoff, or derived work involving a completed card, compare only linked paths against completion commit. Do not compare the whole repository.
- A missing/unavailable commit, path-list mismatch, missing artifact, committed change, or uncommitted change is drift detected by gate/harness and blocks affected lifecycle use. Unrelated paths remain unblocked.
- External harness checks are optional manual/CI evidence, not a required worker handoff.
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

## References

- `references/doc-layout.md`
- `references/kanban-guide.md`
- `references/drift-detect.md`
- `references/blank-project-checklist.md`
- `references/workspace-health-warnings.md`

- `templates/plan.md`
- `templates/spec.md`
- `templates/kanban-task.md`
- `templates/session-handoff.md`
- setup repo `templates/AGENTS.md`
