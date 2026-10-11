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

## Four-phase Initiative lifecycle

For large autonomous work, use one stable Initiative across Discovery, Shaping, Execution, and Decision. Discovery captures problem framing, boundaries, vocabulary, prototype evidence, and open questions, then records approved Shaping handoff. Shaping retains artifact-first Execution Package v2. Execution binds one immutable `execution_batch/v1` attempt to package digest, artifact baseline, Tickets, isolated workspaces, budget, stop conditions, and actor authorization. Integration success opens read-only Decision; it does not complete Initiative.

Decision consumes deterministic evidence and append-only `review_cycle/v1` revisions. Every changed path maps to a Change Group or justified generated/excluded bucket; every nontrivial claim references evidence. `decision_projection/v1` is bounded/redacted and excludes raw logs, secrets, personal data, prompts, and transcripts. Material outcomes use `notification/v1`; transport remains adapter-owned. Human dispositions are `approved_for_mr`, `enhancement_requested`, `rejected`, `resume_execution`, `reshape_required`, or `stopped`. Only `approved_for_mr` completes Ginflow lifecycle and yields provider-neutral `merge_request_intent/v1`; publication/merge remain separate.

Hermes remains identity, Kanban, assignment, dispatch, persistence, and lifecycle authority. Target repositories remain product/canonical-verification authority. Legacy v2 packages and cards without explicit Initiative linkage retain current behavior. TUI, direct Hermes DB access, gateway transport/subscriptions, and provider-specific publication remain deferred.

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

### New Initiative boundary

New governed/autonomous work must use one `initiative/v1` record and the canonical Discovery → Shaping → Execution → Decision lifecycle. Discovery resolves ambiguity and records boundaries. Shaping approves the artifact-first Execution Package v2. Execution authorizes an immutable batch and creates blocked cards. Integration opens read-only Decision; only human `approved_for_mr` yields MR intent. Do not use Work Size, Direct Work, or conditional artifact selection to bypass this lifecycle.

Hermes remains identity, Kanban, assignment, dispatch, persistence, and lifecycle authority. A selected card must contain ID, title, objective, scope, acceptance, workspace, status, assignee, and links. Missing fields block governed execution.

### Legacy v1 compatibility boundary

Active cards created before artifact-first rollout may retain their recorded Work Mode, Work Size, Clarification, Direct Work, and Governed Work route until closure. The legacy route is read-only compatibility guidance; it cannot select or override a new Initiative and cannot weaken package, evidence, isolation, or Decision requirements. The following legacy rules apply only when the card is explicitly an active v1 card.

- Before a legacy card exists, brainstorming and read-only clarification remain conversation-only.
- Eligible legacy XS/S Direct Work may proceed without a card only when every existing eligibility factor is affirmative.
- Legacy M/L/XL or risky work requires a complete card and its conditional Spec/Plan rules.
- Stop and re-route legacy work if scope, risk, ownership, clarity, or verification changes.

### Legacy v1 artifact reference

| Legacy v1 case | Kanban card | Spec | Plan |
| --- | ---: | ---: | ---: |
| Direct Work — eligible XS/S | no | no | no |
| Governed Work — M/L/XL or risky | required | conditional | conditional |
| Clarification/read-only | no | no | no |

New Initiative records never use this table.

Rule: compatibility labels describe active legacy cards only; they are not current Initiative policy.

### Choose artifact level (legacy v1 only)

For an active legacy v1 card, choose Spec when behavior or contract can drift and Plan when ordering, investigation, rollback, coordination, or layered verification matters. New Initiatives always retain the approved package artifacts from Shaping.

Selected card must contain: ID, title, objective, scope, acceptance, workspace, status, assignee, and links. Missing required fields block legacy governed execution until card repair.

### Routing guidance and feedback boundary

When no selected/running card owns the workspace, new work routes to Discovery/Shaping rather than size classification. Legacy v1 routing may use the injected compatibility guidance only when the active card is explicitly identified as v1.

The plugin's candidate skill mapping remains deterministic advisory guidance, not authorization. Hermes must call `skill_view(name='...')`; the plugin never calls it, inspects skill contents, creates cards/artifacts, or mutates Kanban. Canonical output precedence is target-project rules, explicit Initiative/card contract, Ginflow matrix, selected skill, then skill defaults.

Feedback v1 remains a pure legacy Governed Work lifecycle event contract. New Initiative Decision notifications use `notification/v1`; transport remains adapter-owned.

- Before creating a legacy v1 plan, load and follow the `plan` skill.
- Use the Initiative key and package artifact paths for new work; use the Kanban card ID across legacy artifacts.
- Follow linked artifact templates and project-local rules for content quality and boundaries.
- All Ginflow Markdown artifacts use YAML frontmatter at byte 0 for metadata. Specs and plans use `status`, `size`, `scope`, and `owner`; keep lifecycle state in the header and do not duplicate it as body-only `Status:` metadata.

### Legacy routing guidance and feedback boundary

When an explicitly active v1 card has no selected/running owner, use injected routing guidance to evaluate Work Mode, Work Size, Risk Impact, and Direct Work Eligibility. New Initiative work routes through Discovery/Shaping instead.

- affirmative legacy XS/S eligibility → Direct Work (`direct-no-card`);
- known legacy M/L/XL size, actual Risk Impact, or artifact need → Governed Work;
- unresolved legacy routing fact → Clarification with read-only investigation.

Legacy Direct Work eligibility still requires clarity, known cause, genuine XS/S scope, localized reversible change, no actual Risk Impact, no artifact need, known verification, project permission, and an unowned workspace. These checks never authorize a new Initiative.

The plugin's candidate skill mapping is deterministic guidance, not semantic similarity search or authorization. Hermes must call `skill_view(name='...')`; the plugin never calls it, inspects skill contents, creates cards/artifacts, or mutates Kanban. Canonical output precedence is target-project rules, explicit Initiative/card contract, Ginflow matrix, selected skill, then skill defaults. Adapt skill output into the selected canonical artifact rather than duplicating it.

Feedback v1 is a pure legacy Governed Work lifecycle event contract. New Initiative Decision events use `notification/v1`; transport remains adapter-owned.

### New Initiative artifact boundary

Discovery and Shaping may create and revise Initiative artifacts before cards exist, but no product-code mutation or execution dispatch occurs. Use approved package artifacts, immutable batch records, blocked cards, exact evidence, and Decision projections for new work.

Hermes remains the lifecycle authority; Ginflow core validates records and `ginflow-gate` enforces evidence at native transitions.

## Project session startup

### Canonical project context

On the first `/ginflow` load in a project, inspect `.ginflow.yaml` at the current repository root. Do not create a `ginflow` CLI and do not read, migrate, or write `.hermes/ginflow.yaml` or Hermes global config. If the project-local file is absent, show the resolved workspace and current/default Kanban board, then ask whether to use that board or create a new one. A new board requires a non-empty user-provided board name; create it through native Kanban operations before writing the config.

```yaml
version: 1
ginflow:
  board: <Kanban board slug>
  workspace: /absolute/path/to/project
```

`workspace` is the resolved project directory and `board` is the selected board. Resolution precedence is explicit command/API override, `HERMES_KANBAN_BOARD`, the existing `.ginflow.yaml`, then Hermes's active board. The optional `worker` block stores repository-local dispatch defaults: `profile` maps to `kanban_create.assignee`, and `provider`/`model` are passed as explicit `kanban_create` overrides when present. Only board and workspace are required; the worker block is recommended for reproducible dispatch and never invalidates a minimal config.

Before creating a governed card, `/ginflow` checks the configured worker block. When any of `profile`, `provider`, or `model` is absent, it shows the resolved fallback and asks whether to enter the complete block first; entered values are validated and atomically merged into the existing `.ginflow.yaml` before card creation, preserving board, workspace, version, and unrelated keys. Skipped setup leaves the config unchanged and falls back to the current Hermes profile for `assignee`, omitting provider/model so the selected profile's own defaults apply. The prompt repeats at the next card creation until defaults are configured. Explicit per-card user overrides win over repository defaults without rewriting the config. A malformed worker block (wrong type, empty string, or unknown field) blocks card creation without breaking read-only board/workspace routing. A missing config must be initialized by `/ginflow` before governed Kanban work. First-load initialization is agent-procedural: runtime validation and persistence enforce the contract, but no runtime hook or CLI silently initializes a project. A malformed, incomplete, or workspace-mismatched config fails closed; do not overwrite it or silently switch workspace/board. Existing valid config is not rewritten during ordinary skill loading, and project verification only reads it. Gate routing distinguishes missing config (run `/ginflow` to initialize) from invalid config (repair `.ginflow.yaml`); a valid config with no workspace cards remains a normal no-card work-shaping route.

`ginflow.trace` is optional and defaults off. See `references/project-context.md` for the enablement contract (env override, log locations).

Before target-project work, determine whether the request is a new Initiative or active legacy v1 card. New Initiatives follow Discovery/Shaping/Execution/Decision. Legacy card checks below apply only to explicitly identified v1 cards.

1. Confirm workspace points at real target repo.
2. Read local `AGENTS.md` / `.hermes.md`.
3. **Check Kanban board state:**
   - If no Kanban cards exist → route a new request to Discovery/Shaping; active legacy work cannot be inferred.
   - If Kanban cards exist → read progress first (use `kanban_list`/`kanban_show` TOOLS in agent code), then resume selected/active card.
4. For legacy governed work, require and read selected or assigned card. Stop if absent.
5. For legacy governed work, confirm all required card fields and workspace. Stop if incomplete.
6. Read linked spec/plan when present.
7. If selected card is completed, run linked-artifact drift gate before any project action.
8. Inspect git state and run project baseline verification.
9. For legacy governed work, run external ginflow harness against target repo and selected card; do not copy harness into target repo.
10. Report project verification and Ginflow harness separately when legacy governed work applies.
11. Follow routing context injected by `ginflow-gate`; it chooses legacy work mode only when an active v1 card exists.

### Kanban task notifications

Do not launch a `/background` watcher for the selected running card. Kanban task creation from a persistent TUI or gateway session auto-subscribes the originating session when `kanban.auto_subscribe_on_create` is enabled; treat `subscribed: true` in the creation result as confirmation. Terminal events are delivered by the dispatcher, and the subscription is removed after the task reaches `done` or `archived`. If creation does not confirm a subscription, use the normal Kanban notification subscription surface or explicit board reads instead of hidden polling.

Stop when any required input is missing and risk is material.

## Kanban review and completion validation

The `ginflow-gate` completion policy is integrated with native `kanban_request_review` and `kanban_complete` tool calls:

- `pre_tool_call` blocks malformed review requests and completions, linked local spec/plan documents that are not marked completed, mismatched verification/artifact commits, and linked-artifact drift.
- The blocking message lists incomplete linked documents and tells the agent to finalize and commit them before retrying. Documents are never mutated after the card is done.

**Syntax:**

```
kanban_request_review(task_id='<card-id>', summary='<short review request>',
  metadata={'verification_result': {'commit': '<commit>', 'command': 'make test', 'result': 'passed'},
            'artifact_baseline': {'commit': '<commit>', 'paths': ['docs/specs/<CARD-ID>.md']}})
```

- `kanban_complete(task_id='t_abc123', summary='Review approved', metadata={...})`

Reviewer returns an invalid review with native `kanban_request_changes` using a minimal handoff: `reason` (what failed), `evidence` (file:line, failing command, or gate error), and `next_action` (specific worker fix). Hermes returns the card to the original worker under normal dependency gating; review findings never count as blocker-loop failures. `ginflow-gate` validates only Ginflow-specific evidence on request-review and completion transitions; Hermes owns all state transitions.

## Execution contract

- One active card per mutable workspace. Parallel cards are allowed only when each uses an isolated worktree or a different workspace. Hermes dispatcher claim remains the mechanical authority; no public `kanban_claim` tool exists for plugin interception, so atomic workspace-collision enforcement requires Hermes core.
- New Initiative execution requires a selected package-derived card and immutable batch. Legacy v1 execution requires a selected complete card.
- Do not resume, hand off, or derive work from a completed card while its linked-artifact drift is unresolved. Unrelated cards and unlinked project work may continue.
- Stay inside package/card scope and target workspace; preserve exact evidence.
- Use project-native commands and local conventions.
- Block on material ambiguity; do not invent requirements.
- Preserve real verification evidence.

## Definition of done

Work is done only when:

- [ ] Acceptance criteria are satisfied.
- [ ] Relevant project checks ran and passed.
- [ ] Changed files were reviewed against scope.
- [ ] New Initiative records exact Decision/MR evidence; legacy governed work records verification on its Kanban card.
- [ ] Hermes lifecycle status is accurate.
- [ ] Linked artifacts reflect completion or package state.
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

To avoid dispatch racing ahead of linked artifacts, draft card and artifact contents in memory, then create card assigned to the current profile, with complete future links and `--initial-status blocked`. Write and commit linked target artifacts, then run project checks and external candidate-baseline harness. Unblock only after dispatch readiness passes. Current profile loads its configured Ginflow skill; do not force `--skill ginflow`.

If an existing live body is missing required sections, keep it blocked and ask the human to edit the title/body in Kanban dashboard, then rerun harness. The current CLI `hermes kanban edit` only backfills completed-task result/summary/metadata; do not invent a `--body` option. If dashboard repair is unavailable, create corrected replacement card only with human approval and preserve link/comment back to malformed card.

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

Use native `kanban_request_review` for worker handoff and native `kanban_complete` for reviewer completion; both pass through `ginflow-gate`. External CLI harness remains available for manual and CI validation.

Immediately before reporting completion:

1. Run canonical project verification declared by target repo.
2. Read target-repo `git status --short`; use `git diff --stat` when useful.
3. Report only files under selected card workspace.
4. Quote canonical project command and exact fresh result.
5. Record same evidence on selected Kanban card before requesting review or completing it.
6. Worker finalizes every linked local spec/plan with YAML frontmatter at byte 0 declaring `status: completed`, commits those document changes, updates matching verification and artifact-baseline commits, then calls `kanban_request_review` with summary plus metadata. Body status text is ignored.
7. Reviewer independently validates scope, acceptance, diff, and evidence, then calls final `kanban_complete` with `metadata.verification_result` (`commit`, `command`, `result`) and matching `metadata.artifact_baseline` (`commit`, `paths`). `ginflow-gate` validates these synchronously, including exact linked paths and drift, and rejects invalid review or completion transitions.
8. The external CLI harness remains available for manual and CI validation independent of the live plugin gate.
9. Review target workspace using `references/workspace-health-warnings.md`. Record concise findings under `Workspace warnings` on card and in completion report. Warnings do not block by default; promote only when acceptance, canonical verification, security, privacy, data integrity, or restartability is affected. Do not copy warning policy or scanner files into target repo.

Project verification proves product behavior and should be reported truthfully. `ginflow-gate` is evidence authority: it validates card fields, verification metadata, linked artifact baseline, and drift synchronously, then rejects invalid `kanban_request_review` and `kanban_complete` calls. External harness remains optional manual/CI evidence and never substitutes for project verification.

Temporary or ad-hoc checks are not completion evidence unless selected card explicitly targets that temporary artifact. Do not create or report unrelated temporary checks when canonical project verification exists. If canonical verification is unavailable or fails, report blocked/not done.

Live harness examples:

```bash
# Startup/resume: reads task row, body, and latest run metadata directly.
python3 <setup-repo>/skills/ginflow/scripts/validate-harness.py \
  --setup-repo <setup-repo> --target <target-repo> \
  --kanban-task-id "$TASK_ID" --json

# Optional CI/manual candidate check before kanban_request_review.
# ginflow-gate performs authoritative validation during both tool calls.
python3 <setup-repo>/skills/ginflow/scripts/validate-harness.py \
  --setup-repo <setup-repo> --target <target-repo> \
  --kanban-task-id "$TASK_ID" --baseline-commit "$COMMIT" \
  --baseline-path docs/specs/<CARD-ID>.md --json
```

The live harness reads from current board. `--card <json-file>` remains available for fixtures and accepts either normalized Ginflow JSON or saved `hermes kanban show --json` output. It is optional evidence; workers do not need separate harness handoff before calling `kanban_request_review`.

## Harness subsystem mapping

| Subsystem | Ginflow implementation |
| --- | --- |
| Instructions | profile distribution chooses whether to route to `ginflow`; target `AGENTS.md` stores local context |
| State | Hermes Kanban card and Initiative artifacts |
| Verification | project-native canonical command and Decision/card evidence |
| Scope | package/card objective, scope, acceptance, workspace, and isolation |
| Lifecycle | Discovery, Shaping, Execution, Decision; Hermes owns physical transitions |

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
7. Ask Gin to approve content and output path. Use target project's local convention.
8. Write only after approval.

Never infer missing facts from status, chat, OS identity, commit history, or unrelated cards. Never mutate card status, assignee, links, or content during export.

## Drift detection

Use drift detection in 2 layers, in this order:

1. **Project verification first** — target repo declares its own canonical command
   - examples: `./verify.sh`, `make verify`, or project-native command
   - proves project behavior; ginflow does not force script location
- **Repository artifact drift second** — standalone `make verify`
   - checks standalone artifact and harness consistency
   - reports optional runtime integration separately when a consumer provides it

Rule:

- target repo drift check comes first during real work
- standalone `make verify` checks repository artifact and harness health
- do not mix them
- ginflow harness remains in setup/deployed skill and runs externally against target repo; never copy it into target repo

### Completed-card artifact gate

- The worker must commit every linked artifact and prepare truthful `artifact_baseline.commit` and exact target-local linked `artifact_baseline.paths` when calling `kanban_request_review`. Worker may create this baseline commit without human review; stage only exact linked artifacts and intended card-scoped implementation files.
- Never copy harness script into target repo. Report project verification and ginflow harness as separate results.
- `ginflow-gate` is enforcement authority. During `kanban_request_review` and `kanban_complete`, it synchronously validates required card fields, verification metadata, baseline commit, exact linked paths, and artifact drift. Invalid or unavailable evidence rejects transition.
- On startup, resume, handoff, or derived work involving a completed card, compare only linked paths against completion commit. Do not compare whole repository.
- A missing/unavailable commit, path-list mismatch, missing artifact, committed change, or uncommitted change is drift detected by gate/harness and blocks affected lifecycle use. Unrelated paths remain unblocked.
- External harness checks are optional manual/CI evidence, not a required worker handoff.
- Never silently advance completion commit. Do not use per-file SHA fallback.

## Blank project flow

If user starts in blank project:

1. inspect repo for `AGENTS.md` / `.hermes.md`
2. if missing and setup template is available, copy setup repo `templates/AGENTS.md` before project-specific edits
3. add build/test/lint/run commands if known
4. add forbidden areas / deploy rules if known
5. if commands are unknown, leave placeholders and mark them missing
6. retain routing line that sends shared workflow to `ginflow`
7. document one canonical verification command; `verify.sh`, `make verify`, or project-native command are valid
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
