# Atomic completion sequence for `t_example`

The candidate validation has already passed, so freeze and inspect the exact object that was validated:

```python
artifact_baseline = {
    "commit": "abc123",
    "paths": ["docs/briefs/DM-42.md"],
}

metadata = {"artifact_baseline": artifact_baseline}
```

The path list contains exactly the one target-local artifact linked by the card. Do not add other paths, use per-file hashes, recompute the object after validation, or advance the commit.

1. Confirm the fresh canonical-verification evidence and the passing candidate-baseline result are ready to be recorded.
2. Make **one first-and-only completion call**, with the complete metadata included in that call:

```python
kanban_complete(
    task_id="t_example",
    summary="Canonical project verification passed; candidate artifact baseline validated.",
    metadata={
        "artifact_baseline": {
            "commit": "abc123",
            "paths": ["docs/briefs/DM-42.md"],
        }
    },
)
```

Because completion makes the card terminal, do not make a metadata-free/status-only completion call and do not plan to edit or retry the baseline afterward. The first completion call must atomically persist the exact candidate object above in the latest completion-run metadata.

3. After that call succeeds, verify the persisted metadata by rerunning the external harness against the completed live card, with **no** `--baseline-commit` or `--baseline-path` candidate overrides:

```bash
python3 <setup-repo>/skills/ginflow/scripts/validate-harness.py \
  --setup-repo <setup-repo> \
  --target <target-repo> \
  --kanban-task-id t_example \
  --json
```

Add `--board <slug>` only if the task is not on the current board. This post-completion run must read the live card's latest completion-run metadata and confirm:

```json
{
  "artifact_baseline": {
    "commit": "abc123",
    "paths": ["docs/briefs/DM-42.md"]
  }
}
```

Report canonical project verification and this persisted-live-card harness result separately. If the persisted-card run does not pass, report that completion metadata verification failed; do not attempt to repair the terminal card by silently advancing or replacing the baseline.