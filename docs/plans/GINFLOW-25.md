---
status: completed
size: M
scope: Native Hermes implementation-review lifecycle integration test and evidence report
owner: ginb
---

# Native Review Transition Test Fix Implementation Plan

**Status: completed**

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Restore `make test` and verify complete native same-card lifecycle: `ginb` implementation dispatch, `gintary` review dispatch, approval completion, and rejected-review return to `ginb`.

**Architecture:** Keep production code unchanged. Model Hermes state machine instead of bypassing it: dispatcher claims and spawns `ginb`; worker-owned review submission moves same card to `review` and assigns `gintary`; dispatcher claims review and spawns `gintary` with `sdlc-review`; reviewer either completes card or calls `request-changes`, which closes review run and routes same card back to original implementer under parent gating. Use isolated temporary Hermes homes/boards and expose subprocess stdout/stderr for useful failures.

**Tech Stack:** Python standard library, Hermes Kanban CLI, Make, Git.

---

## Current context and assumptions

- Repo: `/Users/gin/dev/gin-harness`
- Branch: `develop`, 14 commits ahead of `origin/develop` at inspection time.
- Canonical verification: `make test`; required pre-completion check: `make lint`.
- Current failure: `plugins/ginflow-gate/test_native_review_transition.py:66`.
- `hermes kanban request-review --help` documents `--force` as override for moving a claimed running task to review when caller does not own its run.
- Test invokes `claim` and `request-review` in independent `subprocess.run` calls. No persistent worker ownership crosses that process boundary.
- Existing uncommitted change in `plugins/ginflow-trace/test_ginflow_trace.py` is unrelated and must remain untouched.
- Generated `plugins/ginflow-gate/__pycache__/__init__.cpython-311.pyc` drift is unrelated. Do not include it in this fix.
- No active `gintary` Kanban card was found. Before execution, create/select complete Ginflow card if work remains governed rather than eligible Direct Work.

## Hermes lifecycle under test

### Implementation stage

1. Card starts `ready`, assigned to `ginb`.
2. Dispatcher atomically claims card, changes status to `running`, records live claim/run, and spawns `ginb` with `HERMES_KANBAN_TASK` and board/workspace context.
3. `ginb` calls `kanban_show`, implements scope, runs canonical verification, and submits same card with `kanban_request_review(summary=..., metadata=..., reviewer="gintary")`.
4. Hermes closes implementation run, clears claim, preserves original implementer, sets status `review`, and assigns card to `gintary`. This is review transition, not block.

### Review stage

5. With `kanban.review_dispatch: true`, dispatcher claims `review` card and spawns `gintary` with bundled `sdlc-review` skill.
6. `gintary` reads card, implementation handoff, comments, diff, and verification evidence; then independently verifies acceptance.
7. **Pass:** reviewer calls `kanban_complete`. Hermes closes review run, sets card `done`, retains completion summary/metadata, and releases dependent children.
8. **Fail:** reviewer calls `kanban_request_changes(reason=...)`. Hermes closes review run, restores original implementer `ginb`, reapplies parent dependency gating, and routes card to `ready` when parents are done or `todo` while any parent remains open. This path does not count as blocking/retry-loop failure.
9. Dispatcher claims rerouted card and spawns `ginb` again with prior runs and review reason in `worker_context`. `ginb` fixes only requested changes, re-verifies, and requests review again. Cycle repeats until approval or genuine external blocker.
10. Genuine dependency/input/capability/transient problems use `kanban_block`, not `request-changes`. `unblock` restores source phase; repeated same-cause blocking can escalate to `triage` under Hermes recurrence guard.

## Proposed approach

1. Make subprocess failures report command output instead of opaque `CalledProcessError` traces.
2. Replace CLI-only cross-process shortcut with lifecycle-aware fixtures/helpers that preserve worker/reviewer identity and run ownership, or use isolated dispatcher runs where practical.
3. Cover success branch: `ginb` running, request review to `gintary`, reviewer claim, reviewer complete, final `done`.
4. Cover change-request branch: reviewer claim, `request-changes`, reassignment to `ginb`, correct `ready`/`todo` gating, redispatch eligibility, and retained reason/history.
5. Keep `--force` only as CLI scripting fallback if identity-preserving worker execution cannot be exercised; do not treat forced transition as canonical lifecycle proof.
6. Run focused tests, lint, then full canonical suite.

### Task 1: Expose Hermes CLI failure details

**Objective:** Make failed integration commands include captured stdout and stderr in assertion output.

**Files:**
- Modify: `plugins/ginflow-gate/test_native_review_transition.py:31-34`
- Test: `plugins/ginflow-gate/test_native_review_transition.py`

**Step 1: Replace opaque helper behavior**

Change `run_hermes` to run without `check=True`, then raise an assertion containing command, exit code, stdout, and stderr when return code is nonzero:

```python
def run_hermes(env, *args):
    command = ["hermes", *args]
    result = subprocess.run(command, env=env, text=True, capture_output=True)
    assert result.returncode == 0, (
        f"command failed ({result.returncode}): {' '.join(command)}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    return result
```

**Step 2: Run focused test and capture expected failure**

Run:

```bash
python3 plugins/ginflow-gate/test_native_review_transition.py
```

Expected: FAIL at `request-review`, now showing Hermes stdout/stderr. Confirm message identifies live claim ownership or explicitly requires `--force`. If message identifies another root cause, stop and revise plan before production changes.

**Step 3: Commit diagnostic improvement separately**

```bash
git add plugins/ginflow-gate/test_native_review_transition.py
git commit -m "test: expose native review command failures"
```

Do not stage unrelated trace-test or `__pycache__` changes.

### Task 2: Cover worker-to-reviewer handoff

**Objective:** Prove `ginb` implementation run hands same card to `gintary` review through native Hermes state.

**Files:**
- Modify: `plugins/ginflow-gate/test_native_review_transition.py:37-74`
- Test: `plugins/ginflow-gate/test_native_review_transition.py`

**Step 1: Write failing lifecycle assertions**

Add assertions for each durable state boundary:

```python
running = show_task(env, task_id)
assert running["status"] == "running"
assert running["assignee"] == "ginb"

reviewed = show_task(env, task_id)
assert reviewed["status"] == "review"
assert reviewed["assignee"] == "gintary"
```

Also assert implementation run closes and carries `verification_result` plus `artifact_baseline` metadata.

**Step 2: Run focused test to verify failure**

```bash
python3 plugins/ginflow-gate/test_native_review_transition.py
```

Expected: FAIL at worker-owned review submission until harness preserves claim/run ownership. Record exact stderr.

**Step 3: Add minimum identity-preserving test harness**

Use Hermes-native dispatcher/worker path if deterministic in temporary home. If direct lifecycle DB helper is required, import installed Hermes code through launcher’s interpreter/path and call same board-layer function used by `kanban_request_review`; do not emulate state transitions manually with SQL.

Required submission semantics:

```python
kanban_request_review(
    task_id=task_id,
    summary="transition verified",
    reviewer="gintary",
    metadata=metadata,
)
```

CLI `--force` remains fallback only for testing CLI escape hatch, not evidence of canonical worker flow.

**Step 4: Run focused handoff assertions**

```bash
python3 plugins/ginflow-gate/test_native_review_transition.py
```

Expected: implementation branch reaches `review`, reviewer is `gintary`, implementation run closed, claim cleared, handoff metadata persisted.

**Step 5: Commit handoff coverage**

```bash
git add plugins/ginflow-gate/test_native_review_transition.py
git commit -m "test: cover worker review handoff"
```

### Task 3: Cover reviewer approval

**Objective:** Prove dispatcher-review claim and reviewer completion move same card to `done`.

**Files:**
- Modify: `plugins/ginflow-gate/test_native_review_transition.py`
- Test: `plugins/ginflow-gate/test_native_review_transition.py`

**Step 1: Add failing approval branch**

After card enters `review`, dispatch/claim it as `gintary`; assert active review run belongs to reviewer. Then invoke native completion with valid Ginflow evidence.

```python
kanban_complete(
    task_id=task_id,
    summary="review approved",
    metadata=metadata,
)
```

**Step 2: Verify RED**

```bash
python3 plugins/ginflow-gate/test_native_review_transition.py
```

Expected: FAIL until reviewer claim/identity path is wired.

**Step 3: Add minimal reviewer execution fixture**

Exercise same dispatcher claim path used for review cards. Confirm review dispatch loads `gintary` and review phase; avoid fake direct status mutation.

**Step 4: Verify GREEN**

Expected assertions:

```python
completed = show_task(env, task_id)
assert completed["status"] == "done"
assert completed["assignee"] == "gintary"
```

Also assert review run closes with approval summary/metadata and any dependent child becomes dispatch-eligible according to parent completion.

**Step 5: Commit approval coverage**

```bash
git add plugins/ginflow-gate/test_native_review_transition.py
git commit -m "test: cover reviewer approval completion"
```

### Task 4: Cover reviewer change request and rework loop

**Objective:** Prove failed review returns same card to `ginb` without block-loop accounting.

**Files:**
- Modify: `plugins/ginflow-gate/test_native_review_transition.py`
- Test: `plugins/ginflow-gate/test_native_review_transition.py`

**Step 1: Create independent rejection card**

Run implementation handoff to `gintary`, then dispatch/claim review as `gintary`.

**Step 2: Add native change request**

```python
kanban_request_changes(
    task_id=rejected_id,
    reason="reason: missing assertion; evidence: test.py:1; next_action: add coverage",
)
```

**Step 3: Assert Hermes continuation state**

When parents are done:

```python
rework = show_task(env, rejected_id)
assert rework["status"] == "ready"
assert rework["assignee"] == "ginb"
```

With unfinished parent, assert `todo`; after parent completion/promotion, assert `ready`. Confirm review run closed, reason retained, prior implementation/review history available, and block recurrence counter unchanged.

**Step 4: Assert redispatch loop**

Dispatch again. Assert card becomes `running` under `ginb`; worker context includes review change reason. Do not complete this branch—the test only needs to prove rework can continue to another review cycle.

**Step 5: Run focused test**

```bash
python3 plugins/ginflow-gate/test_native_review_transition.py
```

Expected:

```text
PASS: native implementation -> review -> approve/request-changes lifecycle
```

**Step 6: Commit rejection coverage**

```bash
git add plugins/ginflow-gate/test_native_review_transition.py
git commit -m "test: cover review change-request loop"
```

### Task 5: Run repository verification

**Objective:** Prove focused fix does not regress setup, lifecycle, plugin, install, or trace behavior.

**Files:**
- No source changes expected.

**Step 1: Run lint**

```bash
make lint
```

Expected: exit 0 and `lint ok`.

**Step 2: Run canonical suite**

```bash
make test
```

Expected: exit 0. Required passing areas include lint, setup test, lifecycle test, all plugin tests, trace tests, and install test.

**Step 3: Inspect scoped diff and workspace health**

```bash
git status --short --branch
git diff --stat HEAD~2..HEAD
git diff HEAD~2..HEAD -- plugins/ginflow-gate/test_native_review_transition.py
```

Expected: fix commits touch only `plugins/ginflow-gate/test_native_review_transition.py`. Existing unrelated workspace changes remain unstaged and unchanged.

**Step 4: Record completion evidence**

For governed work, record exact `make lint` and `make test` results plus completion commit on selected Kanban card, then use native review transition.

### Task 6: Generate final stage-by-stage test report

**Objective:** Produce durable Markdown evidence showing every observed Hermes lifecycle stage and its exact result after test execution.

**Files:**
- Create: `docs/reports/native-review-lifecycle-test-report.md`
- Read evidence from: focused test output, temporary-board task snapshots, run records, comments/events, `make lint`, `make test`, and final Git status

**Step 1: Capture structured lifecycle evidence during focused test**

Make test emit or retain one record per stage without secrets or temporary-home internals:

1. Card created: ID, status, assignee.
2. Dispatcher implementation claim: `ready -> running`, profile `ginb`, run ID when exposed.
3. Worker handoff: review summary, evidence metadata keys, claim closure.
4. Review queued: `running -> review`, assignee `gintary`.
5. Dispatcher reviewer claim: profile `gintary`, review run ID when exposed.
6. Approval branch: reviewer verdict, `review -> done`, completion evidence.
7. Rejection branch: reviewer reason, `review -> ready` or parent-gated `todo`, assignee restored to `ginb`.
8. Rework dispatch: `ready -> running`, profile `ginb`, prior review reason visible.
9. Verification: focused test, `make lint`, `make test` commands and exit results.

Prefer structured Python dictionaries serialized into report inputs over parsing decorative CLI text. Redact absolute temporary directories and environment-specific tokens.

**Step 2: Create report only after tests finish**

Write `docs/reports/native-review-lifecycle-test-report.md` with this exact shape:

```markdown
# Native Review Lifecycle Test Report

- Date/time:
- Git commit:
- Test file:
- Hermes version:
- Overall result: PASS | FAIL

## Stage Log

| # | Actor | Action | Before | After | Assignee | Run/claim evidence | Result |
|---|---|---|---|---|---|---|---|

## Approval Branch

- Dispatcher claim evidence:
- Reviewer verification:
- Completion transition:
- Final card state:

## Change-Request Branch

- Reviewer finding:
- `kanban_request_changes` result:
- Parent-gating result:
- Restored implementer:
- Redispatch result:

## Command Log

| Command | Exit | Result |
|---|---:|---|

## Assertions Verified

- ...

## Deviations / Limits

- ...
```

Every row must report observed data. Use `Not exposed by Hermes output` rather than inventing missing run IDs or timestamps.

**Step 3: Validate report against test evidence**

Check:

- stage order matches board events;
- each state and assignee matches task snapshots;
- approval and rejection branches remain separate;
- command results match fresh process exits;
- no temporary credentials, full environment dump, or raw PII appears;
- report says `FAIL` if any required command failed.

**Step 4: Run Markdown/repository checks**

```bash
make lint
make test
```

Expected: both exit 0. If report creation changes checks, record final rerun—not earlier results—in report.

**Step 5: Commit report with final evidence**

```bash
git add docs/reports/native-review-lifecycle-test-report.md
git commit -m "docs: report native review lifecycle test"
```

Do not stage unrelated trace-test or generated binary changes.

**Step 6: Attach report to governed Kanban completion**

Include absolute report path in `kanban_complete(artifacts=[...])` or review handoff artifact list so subscriber receives real file. Include repository-relative path in metadata for downstream readers.

## Files likely to change

- `plugins/ginflow-gate/test_native_review_transition.py`
- `docs/reports/native-review-lifecycle-test-report.md`

No production files, dependency manifests, architecture diagrams, or trace tests should change.

## Risks and tradeoffs

- Full dispatcher spawning may invoke real model/provider processes. Prefer Hermes board-layer integration plus dispatcher claim selection unless temporary fake profiles/providers already exist in test support.
- Direct SQL mutation would test a shadow workflow, not Hermes. Do not use it.
- `--force` intentionally clears another run’s live claim. It may test CLI escape-hatch behavior separately, but cannot prove canonical worker-owned submission.
- Review failure is not a block. Using `kanban_block` for review findings would engage recurrence accounting and produce wrong lifecycle semantics.
- Better diagnostics slightly expand helper code but prevent hidden stderr during future CLI contract failures.
- Test depends on installed Hermes CLI semantics. If temporary profile registration or installed-code import is unavailable, record exact blocker and revise scope rather than invent state.

## Open questions

- Which installed Hermes board-layer import path is available through launcher environment? Diagnose during Task 2; use actual API, not guessed import.
- Can dispatcher claim selection be invoked without spawning paid model runs? Prefer that seam for deterministic integration coverage.

## Completion checklist

- [ ] `ginb` implementation claim/run proven.
- [ ] Worker-owned request review moves same card to `review` and assigns `gintary`.
- [ ] `gintary` review claim/run proven.
- [ ] Approval moves card to `done` with evidence.
- [ ] Change request restores `ginb` and routes to `ready` or parent-gated `todo`.
- [ ] Redispatch to `ginb` after change request proven.
- [ ] Review rejection avoids block recurrence accounting.
- [ ] Focused native lifecycle test passes.
- [ ] `make lint` passes.
- [ ] `make test` passes.
- [ ] Only intended test file is staged/committed.
- [ ] Existing trace-test edits and generated binary remain untouched.
- [ ] Final report records each observed stage, actor, transition, assignee, and result.
- [ ] Report command log matches fresh focused, lint, and canonical test exits.
- [ ] Report contains no secrets or raw temporary-environment data.
- [ ] Report attached to governed Kanban handoff/completion.
- [ ] Kanban evidence recorded according to Ginflow route.
