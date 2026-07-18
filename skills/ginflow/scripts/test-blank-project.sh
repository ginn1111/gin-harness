#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(cd "$SKILL_DIR/../.." && pwd)"
TARGET="$(mktemp -d /tmp/ginflow-blank-XXXXXX)"
CARD="$(mktemp /tmp/ginflow-card-XXXXXX.json)"
OUTPUT="$(mktemp /tmp/ginflow-output-XXXXXX.txt)"
KEEP_TMP="${KEEP_TMP:-0}"

cleanup() {
  status=$?
  if [[ "$status" -ne 0 || "$KEEP_TMP" == 1 ]]; then
    printf 'blank project retained: %s\n' "$TARGET"
    printf 'agent output retained: %s\n' "$OUTPUT"
  else
    rm -rf "$TARGET"
  fi
  rm -f "$CARD"
  [[ "$KEEP_TMP" == 1 || "$status" -ne 0 ]] || rm -f "$OUTPUT"
  exit "$status"
}
trap cleanup EXIT

git init -q "$TARGET"
python3 - "$SKILL_DIR/scripts/fixtures/card.json" "$CARD" "$TARGET" <<'PY'
import pathlib, sys
source, target, workspace = map(pathlib.Path, sys.argv[1:])
target.write_text(source.read_text().replace("{{WORKSPACE}}", str(workspace)))
PY

task="$(printf '%s\n' 'slugify CLI' 'line counter CLI' 'JSON key sorter CLI' | shuf -n 1)"
prompt="You are in a blank target git repo. Load and follow ginflow. Test card TEST-001 requests: $task. Copy the canonical AGENTS template from $ROOT/templates/AGENTS.md, then tailor only local sections and retain ginflow routing. Create briefs/TEST-001.md. Implement a small standard-library-only solution and tests. Create executable verify.sh using set -eu; document ./verify.sh as canonical verification. Do not create spec or plan unless needed. Do not create session handoff. Before final report run ./verify.sh and git status --short in this target repo. Report only this repo's files and fresh canonical output."

(cd "$TARGET" && env -u TERMINAL_CWD hermes -p gintary -s ginflow -z "$prompt") >"$OUTPUT"

test -f "$TARGET/AGENTS.md"
test -f "$TARGET/briefs/TEST-001.md"
test -f "$TARGET/verify.sh"
test ! -e "$TARGET/session-handoff.md"
grep -q 'come from `ginflow`' "$TARGET/AGENTS.md"
chmod +x "$TARGET/verify.sh"
(cd "$TARGET" && ./verify.sh)
python3 "$SKILL_DIR/scripts/validate-harness.py" --setup-repo "$ROOT" --target "$TARGET" --card "$CARD"

echo "random task: $task"
echo "blank project harness test passed"
