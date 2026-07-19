# Atomic completion for `t_example`

Canonical project verification and candidate-baseline validation have already passed. Construct and inspect the exact payload that was validated **before** changing task state:

```json
{
  "artifact_baseline": {
    "commit": "abc123",
    "paths": [
      "docs/briefs/DM-42.md"
    ]
  }
}
```

Then make exactly one completion call. The **first and only** call must include that metadata atomically:

```python
artifact_baseline = {
    "commit": "abc123",
    "paths": ["docs/briefs/DM-42.md"],
}

kanban_complete(
    task_id="t_example",
    summary="Canonical project verification passed; candidate artifact baseline validated at HEAD abc123.",
    metadata={"artifact_baseline": artifact_baseline},
)
```

Do **not** complete without `metadata`, and do not plan to edit or retry the metadata afterward: completion is terminal. The object passed to `kanban_complete` must be identical to the candidate validated with `--baseline-commit abc123 --baseline-path docs/briefs/DM-42.md`; there are no additional paths and no per-file hashes.

After that single completion succeeds, verify the persisted completion-run metadata by rerunning the external Ginflow harness against the completed live card **without** `--baseline-commit` or `--baseline-path` candidate overrides:

```bash
python3 /home/aioz/personal/agents-hype/skills/ginflow/scripts/validate-harness.py \
  --setup-repo /home/aioz/personal/agents-hype \
  --target "$TARGET_REPO" \
  --kanban-task-id t_example \
  --json
```

Use the card's real absolute target workspace for `TARGET_REPO` (and add `--board <slug>` only if the task is not on the current board). This post-completion run must read the live card's latest completion metadata and confirm exactly:

```json
{
  "artifact_baseline": {
    "commit": "abc123",
    "paths": ["docs/briefs/DM-42.md"]
  }
}
```
