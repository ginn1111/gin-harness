#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TARGET="$(mktemp -d /tmp/ginflow-status-transition-XXXXXX)"
TEST_BOARD="gin-harness-testing"
TASK_ID=""

hermes kanban init >/dev/null
if ! hermes kanban boards list --json | python3 -c 'import json,sys; raise SystemExit(0 if any(row["slug"] == sys.argv[1] for row in json.load(sys.stdin)) else 1)' "$TEST_BOARD"; then
  hermes kanban boards create "$TEST_BOARD" --name "Gin Harness Testing" >/dev/null
fi
cleanup() {
  status=$?
  if [ -n "$TASK_ID" ]; then
    hermes kanban --board "$TEST_BOARD" reclaim "$TASK_ID" >/dev/null 2>&1 || true
    hermes kanban --board "$TEST_BOARD" archive "$TASK_ID" >/dev/null 2>&1 || true
  fi
  rm -rf "$TARGET"
  exit "$status"
}
trap cleanup EXIT

mkdir -p "$TARGET/docs/specs"
cp "$ROOT/templates/AGENTS.md" "$TARGET/AGENTS.md"
printf '# Transition spec\n' > "$TARGET/docs/specs/TRANSITION-1.md"
printf '#!/usr/bin/env bash\nset -eu\nprintf "verify ok\\n"\n' > "$TARGET/verify.sh"
chmod +x "$TARGET/verify.sh"

git init -q "$TARGET"
git -C "$TARGET" config user.name 'Ginflow Test'
git -C "$TARGET" config user.email 'ginflow-test@example.invalid'
git -C "$TARGET" add AGENTS.md docs/specs/TRANSITION-1.md verify.sh
git -C "$TARGET" commit -qm 'initial test fixture'
BODY=$(printf 'Objective: Validate startup before claim\nScope:\n- routing\nAcceptance:\n- valid docs reach running\nLinks:\n- docs/specs/TRANSITION-1.md')
TASK_JSON=$(hermes kanban --board "$TEST_BOARD" create 'TRANSITION-1 — validated startup transition' --body "$BODY" --assignee ginb --workspace "dir:$TARGET" --initial-status blocked --json)
TASK_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$TASK_JSON")

# Real card remains blocked until harness startup validation passes.
hermes kanban --board "$TEST_BOARD" unblock "$TASK_ID" --reason 'startup validation candidate' >/dev/null
STATUS=$(hermes kanban --board "$TEST_BOARD" show "$TASK_ID" --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["task"]["status"])')
test "$STATUS" = ready

python3 - "$ROOT" "$TARGET" "$TASK_ID" "$TEST_BOARD" <<'PY'
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

root, target, task_id = map(Path, sys.argv[1:4])
test_board = sys.argv[4]
spec = importlib.util.spec_from_file_location("harness_core", root / "skills/ginflow/lib/harness_core.py")
assert spec and spec.loader
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
shown = json.loads(subprocess.check_output(["hermes", "kanban", "--board", test_board, "show", str(task_id), "--json"], text=True))
task = shown["task"]
card = {**task, "status": "next", "workspace": f"dir:{target}", "links": ["docs/specs/TRANSITION-1.md"], "objective": "Validate startup before claim", "scope": ["routing"], "acceptance": ["valid docs reach running"]}
gate = core.startup_gate(card, target, target)
assert gate["valid"] is True, gate
assert gate["transition_required"] is True, gate
PY

CLAIM=$(hermes kanban --board "$TEST_BOARD" claim "$TASK_ID" --ttl 60)
STATUS=$(hermes kanban --board "$TEST_BOARD" show "$TASK_ID" --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["task"]["status"])')
test "$STATUS" = running
printf 'validated startup transition passed: %s\n%s\n' "$TASK_ID" "$CLAIM"
