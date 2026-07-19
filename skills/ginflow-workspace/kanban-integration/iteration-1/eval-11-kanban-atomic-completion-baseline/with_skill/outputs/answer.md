Use one candidate baseline object and do not close the card unless the pre-completion harness accepts it.

1. From the target-repository root, rerun its canonical project verification and confirm `git status --short` shows no uncommitted change to any linked artifact. The linked paths below must be the exact target-local paths from the card’s `Links:` section, and `COMMIT` must contain all of them.

2. Validate that candidate against the still-open live card, repeating `--baseline-path` once for every linked document:

```bash
python3 /home/aioz/personal/agents-hype/skills/ginflow/scripts/validate-harness.py \
  --setup-repo /home/aioz/personal/agents-hype \
  --target /absolute/path/to/target-repo \
  --kanban-task-id t_cd34 \
  --baseline-commit COMMIT \
  --baseline-path docs/briefs/t_cd34.md \
  --baseline-path docs/specs/t_cd34.md \
  --baseline-path docs/plans/t_cd34.md \
  --json
```

Replace the example paths with the card’s exact linked local paths; omit paths the card does not link and add another repeated argument for any additional linked document. Add `--board <slug>` if `t_cd34` is not on the current board. If this check blocks, leave the card open.

3. On a passing candidate check, persist the **identical** commit and path list atomically with completion—do not recompute it, change ordering/content, advance to a newer commit, or substitute per-file hashes:

```python
artifact_baseline = {
    "commit": "COMMIT",
    "paths": [
        "docs/briefs/t_cd34.md",
        "docs/specs/t_cd34.md",
        "docs/plans/t_cd34.md",
    ],
}

kanban_complete(
    task_id="t_cd34",
    summary="Canonical project verification passed; completion evidence recorded.",
    metadata={"artifact_baseline": artifact_baseline},
)
```

The `artifact_baseline` object sent to `kanban_complete` must exactly match the candidate represented by the preceding `--baseline-commit` and repeated `--baseline-path` arguments.

4. After completion succeeds, verify what Hermes actually persisted by rerunning the harness against the completed card **without** candidate overrides:

```bash
python3 /home/aioz/personal/agents-hype/skills/ginflow/scripts/validate-harness.py \
  --setup-repo /home/aioz/personal/agents-hype \
  --target /absolute/path/to/target-repo \
  --kanban-task-id t_cd34 \
  --json
```

Again add `--board <slug>` when required. This final run must read the latest completion-run metadata from Hermes and pass with `artifact_baseline.commit == "COMMIT"` and `artifact_baseline.paths` exactly equal to the card’s linked target-local documents. A missing baseline, path mismatch, unavailable commit, missing document, or committed/uncommitted linked-document drift is a blocker and must not be treated as a successful close.