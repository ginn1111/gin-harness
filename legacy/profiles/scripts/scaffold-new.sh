#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1
require_command hermes

profiles=(ginb ginr gins gino)
declare -A descriptions=(
  [ginb]='Builds approved deliveries from the authoritative brief and hands completed work to ginr.'
  [ginr]='Reviews completed deliveries against the authoritative brief and routes passed work to gins.'
  [gins]='Performs final verification and completes or rejects delivery readiness.'
  [gino]='Orchestrates approved L/XL work and decomposes it into M-or-smaller deliveries.'
)

existing="$(hermes profile list 2>/dev/null || true)"
for profile in "${profiles[@]}"; do
  if grep -Eq "(^|[[:space:]])${profile}([[:space:]]|$)" <<<"$existing"; then
    warn "Target profile exists; refusing to overwrite: $profile"
    continue
  fi
  run_or_print hermes profile create "$profile" --no-skills --description "${descriptions[$profile]}"
  if [[ "$APPLY" == "1" ]]; then
    install -m 0644 "$ROOT/profiles/$profile.SOUL.md" "$HOME/.hermes/profiles/$profile/SOUL.md"
    ok "Clean target created — $profile with bundled skills disabled"
    ok "Personality installed — $profile"
  fi
done

if [[ "$APPLY" == "0" ]]; then
  info "Dry run only. Re-run with --apply to create non-existing profiles and install SOUL.md files."
fi
