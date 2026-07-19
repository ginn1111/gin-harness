#!/usr/bin/env bash
set -euo pipefail
# Create durable gintary recovery cards for new task failures.

STATE_DIR="${XDG_STATE_HOME:-$HOME/.hermes/profiles/gintary/state}"
SEEN_FILE="$STATE_DIR/kanban-crash-seen"
mkdir -p "$STATE_DIR"

OUTPUT="$(hermes --profile gintary kanban diagnostics --json 2>/dev/null || true)"
[[ -n "$OUTPUT" && "$OUTPUT" != "[]" && "$OUTPUT" != "null" ]] || exit 0

while IFS=$'\t' read -r task_id title count diagnostic; do
  [[ -n "$task_id" ]] || continue
  fingerprint="$task_id|$count"
  grep -qxF "$fingerprint" "$SEEN_FILE" 2>/dev/null && continue

  body="Objective: Recover crashed task $task_id and restore its Kanban flow.
Scope:
- Inspect original card, worker logs, runs, and diagnostics.
- Identify root cause before changing task state.
- Apply smallest safe recovery and verify resulting worker/task state.
- Never change credentials, security settings, original scope, acceptance, or shared artifacts.
Acceptance:
- Root cause recorded on this recovery card.
- Original task is verified recovered/retrying, or remains blocked with exact human action required.
- Do not complete this card after status-only reporting.
- Send Gin a 1–2 line outcome using: hermes --profile gintary send --to telegram:5743435954 <message>
Original: $task_id — $title
Diagnostic: $diagnostic"

  hermes --profile gintary kanban create \
    "RECOVER $task_id — $title" \
    --body "$body" \
    --assignee gintary \
    --workspace scratch \
    --priority 0 \
    --goal --goal-max-turns 10 \
    --max-retries 2 \
    --created-by kanban-crash-watch \
    --idempotency-key "crash-recovery:$fingerprint" \
    --json >/dev/null

  printf '%s\n' "$fingerprint" >> "$SEEN_FILE"
done < <(python3 -c '
import json, sys
for task in json.load(sys.stdin):
    for diag in task.get("diagnostics", []):
        if diag.get("kind") == "repeated_failures" and diag.get("severity") == "error":
            clean = lambda value: str(value).replace("\t", " ").replace("\n", " ")
            print("\t".join((clean(task["task_id"]), clean(task.get("title", "")), clean(diag.get("count", 0)), clean(diag.get("detail", "")))))
' <<< "$OUTPUT")
