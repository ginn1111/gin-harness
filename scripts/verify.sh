#!/usr/bin/env bash
set -euo pipefail
# Verify setup-repo integrations in existing Hermes-native profiles.
# Usage: ./scripts/verify.sh [--strict] <profile> [profile ...]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FAILED=0
STRICT=0
if [[ "${1:-}" == "--strict" ]]; then STRICT=1; shift; fi
[[ "$#" -gt 0 ]] || { printf 'Usage: %s [--strict] <profile> [profile ...]\n' "$0" >&2; exit 2; }

ok() { printf '✅ %s\n' "$*"; }
warn() { printf '⚠️  %s\n' "$*" >&2; FAILED=1; }
recommend() { printf '💡 %s\n' "$*"; }
command -v hermes >/dev/null || { printf 'Missing: hermes\n' >&2; exit 1; }

REAL_HOME="${HERMES_REAL_HOME:-$(python3 -c 'import os, pwd; print(pwd.getpwuid(os.getuid()).pw_dir)')}"
PROFILES_DIR="$REAL_HOME/.hermes/profiles"
export HOME="$REAL_HOME"
unset HERMES_HOME
existing="$(hermes profile list 2>/dev/null || true)"

echo "===== Hermes Integration Verification ====="
for profile in "$@"; do
  echo
  echo "--- $profile ---"
  if [[ ! "$profile" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then warn "$profile: invalid profile name"; continue; fi
  if ! grep -qw "$profile" <<<"$existing"; then warn "$profile: native profile missing"; continue; fi
  ok "$profile: native profile exists"

  profile_dir="$PROFILES_DIR/$profile"
  [[ -f "$profile_dir/SOUL.md" ]] && ok "$profile: profile-owned SOUL.md present" || warn "$profile: SOUL.md missing"
  [[ -f "$profile_dir/distribution.yaml" ]] && ok "$profile: native distribution manifest present" || recommend "$profile: no distribution.yaml; use Hermes profile install/export for portability"

  ginflow_link="$profile_dir/skills/ginflow"
  if [[ -L "$ginflow_link" && "$(readlink -f "$ginflow_link")" == "$ROOT/skills/ginflow" ]]; then
    ok "$profile: ginflow linked"
  else
    warn "$profile: ginflow integration missing"
  fi

  gate_link="$profile_dir/plugins/ginflow-gate"
  [[ -L "$gate_link" && "$(readlink -f "$gate_link")" == "$ROOT/plugins/ginflow-gate" ]] \
    && ok "$profile: ginflow-gate linked" || warn "$profile: ginflow-gate integration missing"

  cfg="$profile_dir/config.yaml"
  if python3 - "$cfg" "$ROOT" <<'PY'
import sys
from pathlib import Path
import yaml
cfg = yaml.safe_load(Path(sys.argv[1]).read_text()) or {}
root = Path(sys.argv[2])
external = cfg.get("skills", {}).get("external_dirs", [])
assert str(root / "skills") in external
server = cfg.get("mcp_servers", {}).get("codegraph", {})
assert server.get("command") == "codegraph"
assert server.get("args") == ["serve", "--mcp"]
assert "mcp-codegraph" in cfg.get("platform_toolsets", {}).get("cli", [])
assert "ginflow-gate" in cfg.get("plugins", {}).get("enabled", [])
PY
  then ok "$profile: config integrations present"; else warn "$profile: config integrations incomplete"; fi

  if command -v codegraph >/dev/null 2>&1; then
    hermes -p "$profile" mcp test codegraph >/dev/null 2>&1 && ok "$profile: CodeGraph MCP connected" || warn "$profile: CodeGraph MCP connection failed"
  else
    recommend "$profile: CodeGraph CLI absent; MCP configured but unavailable"
  fi
  count=$(hermes -p "$profile" skills list 2>/dev/null | grep -c "enabled" || true)
  [[ "${count:-0}" -gt 0 ]] && ok "$profile: ${count:-0} skills enabled" || warn "$profile: no enabled skills"
done

echo
echo "--- Setup-repo harness ---"
for heading in "Project session startup" "Execution contract" "Definition of done" "Session close and restart" "Optional session handoff export"; do
  grep -q "^## $heading$" "$ROOT/skills/ginflow/SKILL.md" && ok "ginflow: $heading" || warn "ginflow: missing $heading"
done
python3 "$ROOT/skills/ginflow/scripts/validate-harness.py" --setup-repo "$ROOT" >/dev/null && ok "ginflow: static validation passed" || warn "ginflow: static validation failed"
python3 "$ROOT/skills/ginflow/scripts/test-ginflow-gate.py" >/dev/null && ok "ginflow-gate: veto contract passed" || warn "ginflow-gate: veto contract failed or Hermes hook compatibility changed"

drift="$(cd "$ROOT" && git status --porcelain --untracked-files=all 2>/dev/null | cut -c4- | grep -E "^(scripts/|skills/|plugins/|templates/|README\.md$|INSTALL\.md$|Makefile$)" || true)"
if [[ -n "$drift" ]]; then
  if [[ "$STRICT" == 1 ]]; then warn "Uncommitted canonical integration changes detected"; else recommend "Uncommitted canonical integration changes detected (non-fatal)"; fi
else
  ok "No uncommitted integration changes"
fi

[[ "$FAILED" == 0 ]] && ok "All checks passed." || printf '⚠️  Some checks failed.\n' >&2
exit "$FAILED"
