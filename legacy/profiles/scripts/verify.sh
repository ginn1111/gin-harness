#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
require_command hermes
profiles=(ginb ginr gins gino)
failed=0

hermes profile list
for profile in "${profiles[@]}"; do
  echo
  info "Verifying $profile"
  if ! hermes profile show "$profile"; then
    warn "$profile: profile missing or unreadable"
    failed=1
    continue
  fi
  marker="$HOME/.hermes/profiles/$profile/.no-bundled-skills"
  if [[ -f "$marker" ]]; then
    ok "$profile: bundled skills disabled"
  else
    warn "$profile: opt-out marker missing"
    failed=1
  fi
  if [[ -f "$HOME/.hermes/profiles/$profile/SOUL.md" ]]; then
    ok "$profile: personality present"
  else
    warn "$profile: SOUL.md missing"
    failed=1
  fi
  hermes -p "$profile" skills list || { warn "$profile: could not list skills"; failed=1; }
done
exit "$failed"
