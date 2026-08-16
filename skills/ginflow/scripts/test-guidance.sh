#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
skill="$root/skills/ginflow/SKILL.md"
guide="$root/skills/ginflow/references/kanban-guide.md"
for needle in '/background' 'read-only' 'heartbeat-only' 'terminal state' 'non-interactive'; do
  grep -Fq "$needle" "$skill" "$guide"
done
echo "ginflow guidance ok"
