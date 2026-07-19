# Safe pre-dispatch setup for `DM-42`

The critical rule is: **create unassigned, then add a sticky human-input block before assigning `ginb`.** `--initial-status blocked` narrows the setup race, but it is not sufficient by itself when the gateway continually recomputes blocked tasks.

```bash
set -euo pipefail

SETUP_REPO=/abs/path/to/setup-repo
TARGET_REPO=/abs/path/to/target-repo
# Set this only when the task is not on the current board.
# BOARD_ARGS=(--board <board-slug>)
BOARD_ARGS=()

BODY=$(cat <<'EOF'
Objective: <existing objective>
Scope:
- <existing bounded scope>
Acceptance:
- <existing observable acceptance criterion>
Links:
- docs/briefs/DM-42.md
EOF
)

# 1. Create the complete thin card in the real target workspace, but do not
#    assign ginb yet. Capture the Hermes-generated task ID.
TASK_JSON="$(hermes kanban "${BOARD_ARGS[@]}" create \
  'DM-42: <short action title>' \
  --body "$BODY" \
  --workspace "dir:$TARGET_REPO" \
  --initial-status blocked \
  --json)"
TASK_ID="$(printf '%s' "$TASK_JSON" | python3 -c \
  'import json,sys; print(json.load(sys.stdin)["id"])')"

# 2. Immediately make the park sticky. Option placement matters: --kind is
#    an option to `block`, before the task ID.
hermes kanban "${BOARD_ARGS[@]}" block --kind needs_input \
  "$TASK_ID" 'Pre-dispatch card setup in progress; linked artifacts and validation pending'

# 3. A selected, durably parked card now exists, so write the linked target
#    artifact. Add spec/plan files here too if the card links them.
mkdir -p "$TARGET_REPO/docs/briefs"
"${EDITOR:-vi}" "$TARGET_REPO/docs/briefs/DM-42.md"

# The brief must contain the real objective, scope, acceptance criteria, and
# non-goals; do not leave invented details or material TBDs for ginb.

# 4. Run the target repository's canonical verification command first.
cd "$TARGET_REPO"
<target-repo-canonical-verification-command>

# 5. Assign ginb only while the sticky block is still in force.
hermes kanban "${BOARD_ARGS[@]}" assign "$TASK_ID" ginb

# 6. Validate the live card and linked artifact using the external harness.
#    Never copy the harness into the target repository.
python3 "$SETUP_REPO/skills/ginflow/scripts/validate-harness.py" \
  --setup-repo "$SETUP_REPO" \
  --target "$TARGET_REPO" \
  --kanban-task-id "$TASK_ID" \
  "${BOARD_ARGS[@]}" \
  --json

# 7. Only after both checks pass, remove the sticky park and expose the card
#    to the dispatcher.
hermes kanban "${BOARD_ARGS[@]}" unblock \
  --reason 'Brief exists; project verification and Ginflow harness passed; ready for ginb' \
  "$TASK_ID"
```

For a named board, the harness does not use the CLI-style `--board` placement. Replace its invocation with:

```bash
python3 "$SETUP_REPO/skills/ginflow/scripts/validate-harness.py" \
  --setup-repo "$SETUP_REPO" \
  --target "$TARGET_REPO" \
  --kanban-task-id "$TASK_ID" \
  --board <board-slug> \
  --json
```

## Why every transition is safe

1. **Draft before creation, but do not write yet.** Drafting the body and brief contents in memory is allowed pre-card shaping. The future `docs/briefs/DM-42.md` link can therefore be present in the card at creation without violating the rule that target artifacts require a selected card.
2. **Create unassigned with the real workspace.** The returned `$TASK_ID` selects the live card and the `dir:` workspace points at the actual target repository. Omitting `--assignee ginb` is the hard protection during the short creation-to-park interval: even if the gateway recomputes the initial blocked row as ready, it has no worker to dispatch.
3. **Add an explicit sticky `needs_input` block.** `--initial-status blocked` only sets the initial row status; it does not by itself establish the sticky blocked event used by recomputation. The explicit typed block parks the card until an intentional `unblock`, rather than allowing automatic promotion.
4. **Write artifacts only after selection and parking.** Once creation has returned `$TASK_ID`, project artifact creation is inside the Kanban boundary. The sticky park prevents dispatch while `docs/briefs/DM-42.md` is being written and closes the card's temporary dangling future link before any worker sees it.
5. **Verify before exposing work.** Run the target's canonical check first to establish repository readiness. Then assign `ginb` while still parked, because the live harness must validate the final build-ready task row, including its assignee, workspace, exact body labels, acceptance criteria, and linked brief.
6. **Assigning is safe only under the sticky block.** Assignment prepares routing but cannot cause dispatch while the `needs_input` block remains active. Do not assign `ginb` at creation time.
7. **Unblock last.** This is the sole transition that should make the fully prepared, assigned card dispatchable. If artifact writing, canonical verification, or harness validation fails, do not unblock. Leave the task parked, append the failure/blocker and exact next step to the card, repair it, and rerun the failed checks.

Do **not** rely on `--initial-status blocked` alone, do **not** assign `ginb` during creation, and do **not** unblock merely because the brief file exists.