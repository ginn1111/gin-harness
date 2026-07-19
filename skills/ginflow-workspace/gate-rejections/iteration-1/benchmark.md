# Ginflow gate rejection eval iteration 1

| Configuration | Assertions | Pass rate |
|---|---:|---:|
| `ginflow-gate` blocking hook | 8/8 | 100% |

## Rejection coverage

- Reject completion without `metadata.verification_result`.
- Require verification commit, command, and result.
- Require `metadata.artifact_baseline`.
- Require verification and baseline commits to match.
- Reject malformed required card fields.
- Reject unavailable completion commits or linked paths missing from commit.
- Reject linked-artifact drift.
- Fail closed when validation itself errors.

## Concurrency boundary

- Policy is one active card per mutable workspace.
- Different workspaces and isolated worktrees may run concurrently.
- Claim-time workspace collision remains Hermes core work because dispatcher claims do not cross `pre_tool_call`.

## Phase 4.5 — Collapse profile default

- Default integration targets one profile: current profile selected by `hermes profile use <name>`.
- Multiple profiles may install harness independently; switching never creates collaboration or handoff.
- Completion review is mechanical through `ginflow-gate`; no second review profile is implied.
- Live harness uses current board only and exposes no board-selection option.
- Setup and verification remain generic when explicit profile names are supplied.

## Command

`python3 skills/ginflow/scripts/test-ginflow-gate.py`

## Limits

- Completion veto is exercised directly against plugin callback, not through a live mutating card.
- Claim rejection cannot be evaluated until Hermes core adds atomic mutable-workspace collision enforcement.