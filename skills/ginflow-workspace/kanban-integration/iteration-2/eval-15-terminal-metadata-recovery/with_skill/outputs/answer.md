# Terminal completion metadata recovery

## Workflow defect

The defect was the **first** `kanban_complete` call: it moved the live card into a terminal state without including the required path-scoped `artifact_baseline` in completion metadata. The later retry could not repair that non-atomic sequence because completion is terminal; the terminal-task error is therefore expected, not evidence that a second completion should be forced.

## Safe current disposition

Treat the card as **completed in Hermes but invalid as Ginflow authority**. Its missing baseline blocks startup, resume, handoff, or derived work that would rely on that card or its linked artifacts. Do not retry completion, infer a commit from current `HEAD`, invent paths, use per-file hashes, or silently backfill/advance metadata.

Keep the affected lifecycle use blocked until a human explicitly chooses and oversees a supported recovery or reconciliation using verified repository facts. Any recovery must establish the actual completion commit and the exact target-local paths from the card's `Links:` section, rerun canonical project verification and the Ginflow harness as appropriate, and record the decision. Unrelated cards and unrelated paths remain unblocked.

## Rule that prevents recurrence

Completion metadata must be prepared and validated **before** state transition:

1. Ensure every linked target-local artifact is committed.
2. Construct the exact `artifact_baseline` containing that Git completion commit and the exact linked paths.
3. Validate the candidate against the live card with `--kanban-task-id`, `--baseline-commit`, and repeated `--baseline-path` arguments.
4. Pass that identical object as `kanban_complete(metadata={"artifact_baseline": ...})` in the **first and only** completion call.
5. Rerun the harness without candidate overrides to verify that the completed card persisted the metadata.

In short: **validate first, then complete once with metadata atomically; never complete first and attempt metadata recovery through a second completion call.**
