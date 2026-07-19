## Profile `ginb`

Exit: `0`

1. Respect solo constraint: ginb does not dispatch to, collaborate with, or hand off to gintary.

2. Shape request before execution:
   - Confirm real target repo.
   - Inspect read-only context.
   - Choose mode: investigation, implementation, or brainstorming.
   - Choose stable card ID and artifact level: brief always; spec/plan when needed.
   - Draft card and artifact content in memory.

3. Require one Kanban card assigned to ginb. Card must contain ID, title, objective, scope, acceptance, workspace, status, assignee, and links. Keep blocked if incomplete or materially ambiguous.

4. Create card with real target workspace, complete future `Links:`, assignee ginb, and initial status `blocked`. Write linked artifacts in target repo, commit them, run readiness checks, then unblock. No gintary involvement.

5. Start work:
   - Read `AGENTS.md`, `.hermes.md`, selected card, and linked brief/spec/plan.
   - Validate workspace and card fields.
   - Check completed-card artifact drift if applicable.
   - Inspect git state.
   - Run canonical baseline verification.
   - Run external Ginflow harness separately.
   - Stop on blocking input, drift, or ambiguity.

6. Execute alone inside card scope and workspace. Use project-native commands. Keep one active card in mutable workspace. Record real progress and verification evidence on card.

7. Before completion:
   - Satisfy acceptance criteria.
   - Run fresh canonical project verification.
   - Review changed files against scope.
   - Read `git status --short`; use `git diff --stat` if useful.
   - Review workspace-health warnings.
   - Commit linked artifacts and obtain completion commit. If commit permission is absent, stop for human commit.
   - Run external pre-completion harness using exact completion commit and linked paths.

8. Record on card:
   - Verification command and exact result.
   - Changed files, limits, blockers, and workspace warnings.
   - `metadata.verification_result` with commit, command, result.
   - Matching `metadata.artifact_baseline` with commit and exact linked target-local paths.

9. Complete card only after `ginflow-gate` accepts metadata and required fields. Project verification failure blocks completion. Material harness lifecycle failures block affected stage; harness unavailability alone is warning.

10. Report concise completion:
    - Acceptance outcome.
    - Project verification result.
    - Ginflow harness result, separately.
    - Files within selected workspace.
    - Remaining warnings or limits.
    - Accurate completed status.

If interrupted, update Kanban card with outcome, files, checks, blockers, exact next step, and accurate status. Kanban remains durable handoff, still assigned to ginb; no handoff or collaboration with gintary.
[33m⚠ Config issues detected in config.yaml:[0m
  [33m⚠[0m Unknown top-level config key 'known_plugin_toolsets' — it will be ignored
  [2mRun 'hermes doctor' for fix suggestions.[0m


session_id: 20260720_020050_4f6285

## Profile `gintary`

Exit: `0`

Warning: Unknown toolsets: messaging, moa
1. Honor solo constraint: gintary owns work; do not dispatch to, collaborate with, or hand off to ginb.

2. Shape request before execution:
   - Confirm real target-repo workspace.
   - Read local `AGENTS.md` / `.hermes.md`.
   - Classify mode: investigation, implementation, or brainstorming.
   - Choose stable card ID and artifact level.
   - Draft thin card plus brief; add spec/plan when needed.

3. Require one selected Kanban card assigned to gintary. Card must include ID, title, objective, scope, acceptance, workspace, status, assignee, and links. Keep blocked if fields, acceptance, verification path, or material requirements are missing.

4. For new card:
   - Create with complete future `Links:` paths and initial status `blocked`.
   - Write target-repo artifacts under `docs/briefs/`, optionally `docs/specs/` and `docs/plans/`.
   - Commit linked artifacts; lack of commit permission blocks completion.
   - Run readiness harness.
   - Unblock only when dispatch-ready.

5. Start execution:
   - Validate workspace and card.
   - Read linked artifacts.
   - If card was completed, pass path-scoped artifact drift gate first.
   - Inspect Git state.
   - Run canonical baseline verification.
   - Run external Ginflow harness separately.
   - Report both results separately.

6. Execute alone inside card scope and workspace. Use project-native commands. Block on material ambiguity. Keep one active card in mutable workspace. Preserve verification evidence.

7. Before completion:
   - Satisfy acceptance criteria.
   - Run fresh canonical project verification.
   - Review changed files against scope.
   - Read `git status --short`; use `git diff --stat` if useful.
   - Review workspace-health warnings.
   - Run pre-completion external harness with completion commit and exact linked artifact paths.

8. Record same evidence on card: outcome, changed files, exact verification command/result, blockers or limits, workspace warnings, completion commit, `metadata.verification_result`, and matching path-scoped `metadata.artifact_baseline`.

9. Complete only if project checks pass, card/harness blockers are clear, linked artifacts are committed, status is accurate, and repo is restartable. Harness unavailability is warning; failed or unavailable canonical verification means not done.

10. Report concise completion: acceptance met, scoped files, canonical command plus exact result, separate harness result, workspace warnings, and remaining limits.

If interrupted, update card with outcome, changed files, checks, blockers, exact next step, and accurate status. Resume later from card and linked artifacts—still as gintary, without ginb.
[33m⚠ Config issues detected in config.yaml:[0m
  [33m⚠[0m Unknown top-level config key 'known_plugin_toolsets' — it will be ignored
  [33m⚠[0m Unknown top-level config key 'profile' — it will be ignored
  [2mRun 'hermes doctor' for fix suggestions.[0m


session_id: 20260720_020035_618fc0
