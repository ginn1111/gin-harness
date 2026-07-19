# Terminal completion without `artifact_baseline`

## Workflow defect

The root defect was the **first** `kanban_complete` call. Completion is a terminal transition, so the worker needed to treat the status change and its completion metadata as one atomic operation. By completing the card without `metadata.artifact_baseline`, it produced a completed card with no valid path-scoped completion authority. A second `kanban_complete` call is not a metadata patch mechanism; the terminal-task error is expected once the first call has closed the task.

## Safe current disposition

Treat the card as **completed but invalid as authority** for startup, resume, handoff, or work derived from that card. The missing baseline is a blocker for those uses, while unrelated cards and unlinked work remain unaffected.

Do not infer a baseline from current `HEAD`, later repository state, per-file hashes, or what the worker believes it intended to send. Keep the authority gate blocked until an explicit human-approved recovery establishes the exact completion commit and exact linked target-local paths from trustworthy evidence, or the card is reopened/reconciled under the supported workflow, reverified, and completed with a valid baseline. If the original completion baseline cannot be established, record that uncertainty rather than silently inventing or advancing one.

## Rule that prevents recurrence

Before the **first and only** completion call:

1. Commit every linked target-local artifact.
2. Construct the candidate `artifact_baseline` from that Git commit and the card's exact linked paths.
3. Validate that candidate against the live card with the external harness.
4. Pass the identical object in `kanban_complete(metadata={"artifact_baseline": ...})` on the same call that makes the task terminal.
5. Rerun the harness against the completed card without candidate overrides to verify the persisted completion-run metadata.

Never complete first and plan to add completion metadata with a retry afterward.