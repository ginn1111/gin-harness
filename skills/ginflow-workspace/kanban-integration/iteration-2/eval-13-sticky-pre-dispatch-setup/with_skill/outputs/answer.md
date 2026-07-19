# Safe sticky pre-dispatch setup for DM-42

Use the real target repository, and choose the stable human-facing key `DM-42` before creation. Draft both the thin card body and the brief contents in memory first, but do **not** write the brief before a card exists.

```bash
set -euo pipefail

SETUP_REPO=/absolute/path/to/setup-repo
TARGET_REPO=/absolute/path/to/target-repo

BODY='Objective: <the already-agreed objective>
Scope:
- <the already-agreed bounded scope and exclusions>
Acceptance:
- <the already-agreed observable completion check>
Links:
- docs/briefs/DM-42.md'

# 1. Create the card UNASSIGNED, in the real target workspace.
# --initial-status blocked narrows the setup window, but is not the sticky park.
TASK_JSON="$({
  hermes kanban create \
    --body "$BODY" \
    --workspace "dir:$TARGET_REPO" \
    --initial-status blocked \
    --json \
    'DM-42: <short action title>'
})"
TASK_ID="$(printf '%s\n' "$TASK_JSON" | jq -er '.id // .task.id')"
printf 'Created %s\n' "$TASK_ID"

# 2. Immediately create the sticky human-input block.
# Important: --kind is before the positional task ID.
hermes kanban block --kind needs_input \
  "$TASK_ID" 'Card setup in progress'

# 3. Only now, with a selected and parked card, write every linked artifact.
cd "$TARGET_REPO"
mkdir -p docs/briefs
"${EDITOR:-vi}" docs/briefs/DM-42.md

# The brief must contain at least an aligned Objective, Scope,
# Acceptance criteria, and Non-goals; write any additionally linked
# spec/plan now as well.

# 4. Run the target repository's canonical checks first.
<target-repo-canonical-verification-command>

# 5. Assign ginb while the sticky block is still present.
hermes kanban assign "$TASK_ID" ginb

# 6. Validate the live card and linked artifact externally.
python3 "$SETUP_REPO/skills/ginflow/scripts/validate-harness.py" \
  --setup-repo "$SETUP_REPO" \
  --target "$TARGET_REPO" \
  --kanban-task-id "$TASK_ID" \
  --json

# 7. Only after the project check and harness both establish dispatch
# readiness, remove the setup block.
hermes kanban unblock \
  --reason 'Card, linked artifacts, project checks, and Ginflow harness are ready' \
  "$TASK_ID"
```

If the task is on a non-current board, add `--board "$BOARD"` to the harness and place it at Kanban level for direct commands, for example `hermes kanban --board "$BOARD" create ...`. Apply the same Kanban-level placement to the other direct card operations where board selection is needed.

## Why each transition is safe

1. **Draft first, create unassigned:** The future `docs/briefs/DM-42.md` path can be present at creation without violating the no-pre-card-artifact rule. Omitting `--assignee ginb` is essential: even if the continuously recomputing gateway changes status during the short setup window, there is no worker to dispatch.
2. **Initial blocked status plus explicit sticky block:** `--initial-status blocked` only narrows the transient window. It does **not** emit the sticky blocked event, so the gateway may auto-promote a card that has only that initial status. `hermes kanban block --kind needs_input "$TASK_ID" ...` emits the required sticky event and keeps the card parked through later recomputation. The option must precede the task ID.
3. **Write artifacts only after selection and parking:** Once creation returns `$TASK_ID`, there is a selected live card, satisfying the Kanban boundary. The temporary setup block is therefore not artifact work without a card. Writing the brief now also closes the dangling future link before dispatch.
4. **Verify before exposing the card:** Canonical project verification proves repository readiness. The external Ginflow harness then reads the live task row/body and confirms the real workspace, required labels, acceptance, assignee, and linked brief. The harness remains in the setup repo and is not copied into the target repo.
5. **Assign while still blocked:** Assigning `ginb` only after artifacts exist prevents ginb from receiving an incomplete handoff. Assignment itself cannot start the worker because the sticky `needs_input` block is still active.
6. **Unblock last:** Unblocking is the single transition that makes the fully assigned card dispatchable. It happens only after artifact creation, canonical verification, assignment, and successful harness validation. If writing or either validation fails, do not unblock; leave the card parked, record the failure/blocker, and repair it before rerunning validation.

Do not rely on `--initial-status blocked` alone, do not assign ginb during creation, and do not unblock merely because the brief file now exists.