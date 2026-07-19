## Profile `ginb`

Exit: `0`

Use harness as external workflow gate for target repo. Do not copy it into project.

Operating model:

- Current executor: `ginb`.
- `ginb` owns selected card from startup through completion.
- Do not contact, assign to, dispatch to, or wait for `gintary` by default.
- Another profile becomes relevant only when user explicitly assigns work there or parallel work gets separate card plus isolated worktree/workspace.
- One active card per mutable workspace. Dispatcher claim is mechanical authority.

Before execution, `ginb` must:

1. Confirm workspace is real target repo, not setup repo.
2. Read target `AGENTS.md` and `.hermes.md`.
3. Require one selected/assigned Kanban card.
4. Validate ID, title, objective, scope, acceptance, workspace, status, assignee, and links.
5. Read linked brief/spec/plan.
6. Check completed-card artifact drift when applicable.
7. Inspect git state and run canonical project baseline verification.
8. Run external Ginflow harness against target repo and card.
9. Report project verification and harness separately.

Missing card, wrong assignee/workspace, incomplete fields, material ambiguity, or missing verification path: stop and ask Gin. Do not wait for `gintary`.

During work:

- Stay inside card scope and workspace.
- Keep card assigned to `ginb`.
- Record progress, blockers, changed files, checks, and next step on card.
- Use isolated worktree/workspace for any parallel card.

Completion:

- Run canonical project verification first.
- Review scoped changes and workspace warnings.
- Run external harness second.
- Record exact verification result and path-scoped artifact baseline on card.
- Complete only when acceptance and lifecycle gates pass.

Kanban card plus linked target-repo artifacts form durable handoff. Session transcript and memory are supporting context only. `gintary` does not need contact, assignment, or synchronization unless Gin deliberately transfers or separately assigns work.
[33m⚠ Config issues detected in config.yaml:[0m
  [33m⚠[0m Unknown top-level config key 'known_plugin_toolsets' — it will be ignored
  [2mRun 'hermes doctor' for fix suggestions.[0m


session_id: 20260720_020011_a79765

## Profile `gintary`

Exit: `0`

Warning: Unknown toolsets: messaging, moa
Use harness as profile `gintary`, operating directly in real target repo—not setup repo.

Operating model:

- `gintary` owns current task execution. Do not contact, assign, or wait for `ginb` by default.
- Hermes Kanban card is authority and durable handoff—not chat, memory, or another profile.
- Before execution: confirm target workspace, read local rules, select one complete card assigned to `gintary`, read linked artifacts, inspect Git state, run baseline project verification, then external Ginflow harness.
- No selected complete card means stop. Pre-card brainstorming and read-only shaping allowed; implementation investigation, edits, dispatch, and verification blocked.
- One active card per mutable workspace. Parallel work requires isolated worktree or different workspace.
- Keep task inside card objective, scope, acceptance, workspace, and links. Block on material ambiguity.
- Store brief/spec/plan in target repo under card ID paths. Harness stays external in setup repo.
- Completion requires acceptance met, canonical project checks passed, scope reviewed, evidence recorded on card, accurate status, committed linked artifacts, and successful lifecycle gate.
- Report project verification and Ginflow harness separately. Harness-unavailable is warning; missing card/workspace/acceptance/artifacts or artifact drift blocks affected stage.
- Unfinished work resumes from card, linked artifacts, repo state, and local rules.

Use `ginb` only when human explicitly selects or assigns work to it, or gives it separate card plus isolated workspace. Do not coordinate with, auto-dispatch to, or wait for `ginb` merely because profile exists.
[33m⚠ Config issues detected in config.yaml:[0m
  [33m⚠[0m Unknown top-level config key 'known_plugin_toolsets' — it will be ignored
  [33m⚠[0m Unknown top-level config key 'profile' — it will be ignored
  [2mRun 'hermes doctor' for fix suggestions.[0m


session_id: 20260720_015954_6c8176
