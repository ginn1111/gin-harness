# Live Kanban startup adapter for `t_ab12`

**Do not create a separate normalized card JSON.** The live Hermes task is the source of truth. Run the Ginflow harness from the setup repository, point it at the real target repository, and identify the live task and its board:

```bash
python3 /home/aioz/personal/agents-hype/skills/ginflow/scripts/validate-harness.py \
  --setup-repo /home/aioz/personal/agents-hype \
  --target /absolute/path/to/the/real/target-repo \
  --kanban-task-id t_ab12 \
  --board product \
  --json
```

Replace `/absolute/path/to/the/real/target-repo` with the task's actual target-repository path. Keep the harness external; do not copy it or a shadow card file into the target repository. In the startup sequence, first read the target's `AGENTS.md`/`.hermes.md`, confirm the selected task and linked artifacts, inspect Git state, and run the target's canonical baseline verification. Then run the command above and report the project verification and Ginflow harness result separately before resuming work.

## Integration path

1. `validate-harness.py` receives `--kanban-task-id t_ab12` and `--board product`.
2. It executes:

   ```bash
   hermes kanban --board product show t_ab12 --json
   ```

3. It parses that live JSON and internally normalizes it into Ginflow's card shape in memory.
4. It validates the normalized card against the real target repository supplied by `--target`, including linked briefs, local instructions, the documented verification command, and—when applicable—the completed-card artifact baseline and linked-artifact drift.

`--card <json-file>` exists only for fixtures or previously saved command output; it is not the live-task integration path and is unnecessary here.

## Where Ginflow reads each field

From the top-level `task` object returned by `hermes kanban show --json`:

- **ID**: `task.id`
- **Title**: `task.title`
- **Status**: `task.status`
- **Assignee**: `task.assignee`
- **Workspace**: `task.workspace_kind` plus `task.workspace_path`; for `dir` or `worktree` with a path, the harness normalizes these to `<kind>:<path>` (for example, `dir:/absolute/path/to/repo`).

From `task.body`, using the exact section labels:

- **Objective**: content under `Objective:`
- **Scope**: items under `Scope:`
- **Acceptance**: items under `Acceptance:`
- **Links**: items under `Links:`

The parser accepts the label on a plain line or Markdown heading, treats label matching case-insensitively, and collects `- ` or `* ` list items. Keep the canonical labels exactly as documented to avoid ambiguity.

The harness scans `runs` from newest to oldest and uses the latest run containing a metadata object:

- If `metadata.ginflow` contains `objective`, `scope`, `acceptance`, or `links`, those values override the corresponding body-derived values.
- **`artifact_baseline`** is read from that latest run's `metadata.artifact_baseline`. This is completion metadata, required for a completed card when target-local linked docs are guarded; it is not a second card document. The expected shape is a Git completion `commit` and `paths` exactly matching the linked target-local docs.

Thus `t_ab12` already has the correct integration shape: normal task fields for ID/title/workspace/status/assignee, canonical body sections for objective/scope/acceptance/links, and latest-run metadata for any completion baseline.