## Profile `ginb`

Exit: `0`

Use harness as ginb, current execution profile.

Operating model:

- ginb owns task execution in real target repo.
- Do not contact, assign to, or wait for gintary by default.
- Current profile loads configured Ginflow skill. Do not force another profile or `--skill ginflow`.
- Hermes Kanban selected card is authority for task, assignee, status, workspace, scope, acceptance, and links.
- One active card per mutable workspace. Parallel work needs isolated worktree or different workspace.
- Kanban dispatcher claim is mechanical authority. No profile-to-profile coordination substitutes for it.

Before work, ginb must:

1. Confirm workspace is real target repo, not setup repo.
2. Read `AGENTS.md` and `.hermes.md`.
3. Require one selected/assigned, complete Kanban card assigned to ginb.
4. Validate ID, title, objective, scope, acceptance, workspace, status, assignee, and links.
5. Read linked brief/spec/plan.
6. Check completed-card artifact drift when applicable.
7. Inspect git state and run canonical baseline verification.
8. Run external Ginflow harness against target repo/card.
9. Report project verification and harness separately.

If card is absent, incomplete, assigned to gintary, points at wrong workspace, lacks acceptance/verification path, or has unresolved completed-card drift: stop. Ask Gin to select, repair, reassign, or resolve card. Do not contact gintary or wait for it unless Gin explicitly chooses cross-profile coordination.

During work, ginb stays inside card scope/workspace, records progress and evidence on card, and blocks on material ambiguity.

Completion requires passing canonical project checks, scope review, recorded evidence, accurate Kanban state, restartable repo, explicit limits, and external harness validation. Harness warnings do not replace project verification; lifecycle-critical harness failures block completion.
[33m⚠ Config issues detected in config.yaml:[0m
  [33m⚠[0m Unknown top-level config key 'known_plugin_toolsets' — it will be ignored
  [2mRun 'hermes doctor' for fix suggestions.[0m


session_id: 20260720_015954_b51aea

## Profile `gintary`

Exit: `0`

Warning: Unknown toolsets: messaging, moa
Use harness from setup repo externally against real target repo. Do not use setup repo as code workspace or copy harness into target repo.

Operating model:

- Active executor: `gintary`.
- Do not contact, assign to, or wait for `ginb` by default.
- Current profile loads configured Ginflow skill; do not force `--skill ginflow`.
- Kanban card is durable authority and handoff—not chat, memory, or another profile.

Before execution:

1. Confirm workspace is real target repo.
2. Read target `AGENTS.md` and `.hermes.md`.
3. Shape task if needed, then require one selected/assigned Kanban card.
4. Card must contain ID, title, objective, scope, acceptance, workspace, status, assignee, and links.
5. Assignee should be `gintary` for current-profile execution.
6. Read linked brief/spec/plan.
7. Check completed-card artifact drift when applicable.
8. Inspect git state; run canonical project baseline verification.
9. Run external Ginflow harness against target repo and `$TASK_ID`.
10. Report project verification and harness separately.

Execution starts only after complete card exists. One active card per mutable workspace; parallel work requires isolated worktree or different workspace.

Contact or assign `ginb` only when user explicitly chooses cross-profile delegation or card is deliberately assigned there. Then Kanban card, linked artifacts, workspace, and status provide handoff. Do not coordinate through inferred chat state. If `ginb` owns card, `gintary` should not mutate same workspace or wait implicitly; either select work assigned to `gintary`, use isolated workspace, or ask user to resolve ownership.

Stop when card absent/incomplete, repo wrong, acceptance or verification path missing, requirement materially unclear, or completed-card drift unresolved.
[33m⚠ Config issues detected in config.yaml:[0m
  [33m⚠[0m Unknown top-level config key 'known_plugin_toolsets' — it will be ignored
  [33m⚠[0m Unknown top-level config key 'profile' — it will be ignored
  [2mRun 'hermes doctor' for fix suggestions.[0m


session_id: 20260720_015954_5b83c2
