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

## Command

`python3 skills/ginflow/scripts/test-ginflow-gate.py`

## Limits

- Completion veto is exercised directly against plugin callback, not through a live mutating card.
- Claim rejection cannot be evaluated until Hermes core adds atomic mutable-workspace collision enforcement.