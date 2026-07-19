## Profile `ginb`

Exit: `0`

1. Honor constraint: ginb works alone. Do not dispatch, hand off to, or collaborate with gintary.

2. Shape task before execution:
   - Confirm real target-repo workspace.
   - Read-only inspect enough to choose mode and size.
   - Draft objective, scope, acceptance, exclusions, and `Links:`.
   - Choose stable card ID and required brief; add plan/spec when needed.

3. Require one Kanban card assigned to ginb. Card must include ID, title, objective, scope, acceptance, workspace, status, assignee, and links. If absent or incomplete, stop and ask Gin to create/repair it. Keep malformed card blocked.

4. For new card:
   - Create blocked, assigned to ginb, with future artifact paths.
   - Write linked artifacts in target repo.
   - Commit artifacts; lack of commit permission blocks readiness.
   - Run project checks and candidate-baseline harness.
   - Unblock only after dispatch readiness passes.

5. Start work:
   - Read `AGENTS.md`, `.hermes.md`, selected card, and linked artifacts.
   - Check completed-card artifact drift if relevant.
   - Inspect git state.
   - Run canonical baseline verification first.
   - Run external Ginflow harness separately.
   - Stop on wrong repo, material ambiguity, missing acceptance, missing verification path, or blocking drift.

6. Execute inside card scope and workspace only. Use project-native commands. Keep one active card in mutable workspace. Record progress/evidence on card. No gintary involvement.

7. Complete:
   - Satisfy acceptance.
   - Run fresh canonical project verification.
   - Review changed files against scope and inspect `git status --short`.
   - Run external pre-completion harness with completion commit and exact linked artifact paths.
   - Review workspace-health warnings.
   - Record project result, harness result, warnings, limits, `verification_result`, and matching `artifact_baseline` on card.
   - Complete card only if blocking gates pass.

8. Report concise results:
   - Changed files under selected workspace.
   - Exact canonical command and fresh result.
   - Ginflow harness result separately.
   - Workspace warnings and remaining limits.
   - Accurate final Kanban status.

If unfinished or blocked, update card with outcome, changed files, checks, blocker, exact next step, and accurate status. Kanban remains durable handoff, but no handoff to gintary.
[33m⚠ Config issues detected in config.yaml:[0m
  [33m⚠[0m Unknown top-level config key 'known_plugin_toolsets' — it will be ignored
  [2mRun 'hermes doctor' for fix suggestions.[0m


session_id: 20260720_020031_3fbef6

## Profile `gintary`

Exit: `0`

Warning: Unknown toolsets: messaging, moa
1. Honor constraint: profile `gintary` works alone. Do not dispatch, collaborate with, assign to, or request input from `ginb`.

2. Shape request before execution:
   - Confirm real target repo.
   - Choose investigation, implementation, or brainstorming.
   - Define objective, scope, acceptance, exclusions, workspace, and needed brief/spec/plan.
   - Read-only inspection and drafting allowed here.

3. Require one selected Kanban card assigned to `gintary`. Card must have ID, title, objective, scope, acceptance, workspace, status, assignee, and links. If absent or incomplete, stop; keep blocked and ask Gin for repair.

4. Create linked artifacts safely:
   - Draft card and artifact content first.
   - Create card assigned to `gintary`, initially `blocked`, with future `Links:` paths.
   - Write target-repo brief always; add spec/plan when required.
   - Commit linked artifacts, run readiness checks, then unblock.
   - If commit permission missing, stop for human commit.

5. Start project work:
   - Verify workspace matches card.
   - Read `AGENTS.md`, `.hermes.md`, card, and linked artifacts.
   - Run completed-card drift gate if applicable.
   - Inspect git state.
   - Run canonical baseline verification.
   - Run external Ginflow harness separately.
   - Stop on material ambiguity, missing verification path, wrong workspace, card defect, or blocking drift.

6. Execute only card scope in that workspace. Use project-native commands and local rules. Keep one active card per mutable workspace. Record progress and evidence on card. No involvement from `ginb`.

7. Complete only after:
   - Acceptance passes.
   - Canonical project verification passes.
   - Changed files match scope.
   - Workspace warnings reviewed.
   - Linked target artifacts are committed.
   - Pre-completion harness validates exact completion commit and linked paths.

8. Record on card:
   - Verification command and exact result.
   - Completion commit.
   - Exact `artifact_baseline.paths`.
   - Workspace warnings.
   - Remaining limits or blockers.
   - Accurate final status.

9. Run `kanban_complete` with matching `metadata.verification_result` and `metadata.artifact_baseline`. Report project verification and Ginflow harness separately. If canonical verification fails or required lifecycle gate blocks, report not done and leave card status accurate.

10. If unfinished, card becomes durable handoff: record outcome, changed files, checks, blockers, and exact next step. Future `gintary` session resumes from card, artifacts, local rules, and repo state—not from `ginb` or chat history.
[33m⚠ Config issues detected in config.yaml:[0m
  [33m⚠[0m Unknown top-level config key 'known_plugin_toolsets' — it will be ignored
  [33m⚠[0m Unknown top-level config key 'profile' — it will be ignored
  [2mRun 'hermes doctor' for fix suggestions.[0m


session_id: 20260720_020031_4e908c
