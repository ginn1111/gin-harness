#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
skill="$root/skills/ginflow/SKILL.md"
guide="$root/skills/ginflow/references/kanban-guide.md"
for needle in 'Kanban task notifications' 'auto-subscribes' 'subscribed: true' 'dispatcher' 'hidden polling'; do
  grep -Fq "$needle" "$skill" "$guide"
done
if grep -Fq '/background Watch Kanban task' "$skill" "$guide"; then
  echo "legacy background watcher guidance remains" >&2
  exit 1
fi
echo "ginflow guidance ok"
