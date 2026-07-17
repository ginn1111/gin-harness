#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1
require_command git
TARGET="$HOME/.hermes/shared-skills/mattpocock-skills"
REPO="https://github.com/mattpocock/skills.git"

if [[ -d "$TARGET/.git" ]]; then
  info "Shared skill repository already exists: $TARGET"
else
  run_or_print mkdir -p "$HOME/.hermes/shared-skills"
  run_or_print git clone "$REPO" "$TARGET"
fi

if [[ "$APPLY" == "1" ]]; then
  chmod -R a-w "$TARGET"
  ok "Shared skills installed read-only — $TARGET"
else
  info "Dry run only. Re-run with --apply to clone and make the shared repository read-only."
fi
