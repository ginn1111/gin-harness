#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
require_command hermes
OUT="${1:-$ROOT/reports/profile-inventory.txt}"
mkdir -p "$(dirname "$OUT")"
{
  echo "# Hermes profile inventory"
  echo "# Read-only discovery; no profiles were changed."
  echo
  hermes profile list
} | tee "$OUT"
ok "Existing profiles discovered — migration inventory recorded at $OUT"
echo
echo "Next: map each discovered profile to ginb, ginr, gins, gino using an existing name, NEW, or SKIP."
