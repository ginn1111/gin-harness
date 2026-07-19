#!/usr/bin/env bash
set -euo pipefail
# verify.sh — Verify deployed global profiles match setup repo.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FAILED=0
STRICT=0
case "${1:-}" in
  "") ;;
  --strict) STRICT=1 ;;
  *) printf 'Usage: %s [--strict]\n' "$0" >&2; exit 2 ;;
esac

info()  { printf 'ℹ️  %s\n' "$*"; }
ok()    { printf '✅ %s\n' "$*"; }
warn()  { printf '⚠️  %s\n' "$*" >&2; FAILED=1; }
recommend() { printf '💡 %s\n' "$*"; }
die()   { printf '❌ %s\n' "$*" >&2; exit 1; }
require_command() { command -v "$1" >/dev/null 2>&1 || die "Missing: $1"; }
require_command hermes

REAL_HOME="$(getent passwd "$(whoami)" 2>/dev/null | cut -d: -f6)"
REAL_HOME="${REAL_HOME:-$HOME}"
HERMES_PROFILES_DIR="$REAL_HOME/.hermes/profiles"
# Profile-scoped sessions may override HOME and HERMES_HOME. Verification must
# inspect the machine's named-profile registry, not a nested profile home.
export HOME="$REAL_HOME"
unset HERMES_HOME

profiles=(gintary ginb)
declare -A expected_descriptions
while IFS='|' read -r name description; do
  expected_descriptions["$name"]="$description"
done < <(python3 - "$ROOT/config/profiles.yaml" <<'PY'
import sys, yaml
with open(sys.argv[1]) as f:
    profiles = (yaml.safe_load(f) or {}).get("profiles", {})
for name, config in profiles.items():
    print(f"{name}|{config.get('description', '')}")
PY
)

echo "===== Global Profile Verification ====="

# === 1. Profile existence ===
echo ""
echo "--- Profile existence ---"
existing=$(hermes profile list 2>/dev/null || true)
for p in "${profiles[@]}"; do
  if grep -qw "$p" <<<"$existing"; then ok "$p: exists"; else warn "$p: NOT FOUND"; fi
done

# === 2. Routing descriptions ===
echo ""
echo "--- Routing descriptions ---"
for p in "${profiles[@]}"; do
  actual_description="$(hermes profile describe "$p" 2>/dev/null || true)"
  if [[ "$actual_description" == "${expected_descriptions[$p]:-}" ]]; then
    ok "$p: description matches registry"
  else
    warn "$p: description drift (run ./scripts/setup.sh --apply)"
  fi
done

# === 3. SOUL.md ===
echo ""
echo "--- SOUL.md (symlink check) ---"
for p in "${profiles[@]}"; do
  link="$HERMES_PROFILES_DIR/$p/SOUL.md"
  source="$ROOT/profiles/$p.SOUL.md"
  if [[ -L "$link" ]]; then
    target=$(readlink "$link")
    if [[ "$target" == "$source" ]]; then
      ok "$p: SOUL.md symlinked to repo"
    else
      warn "$p: SOUL.md symlinked to wrong target: $target (expected $source)"
    fi
  elif [[ -f "$link" ]]; then
    warn "$p: SOUL.md is a regular file (not symlink)"
  else
    warn "$p: SOUL.md missing"
  fi
done

# === 4. Config ===
echo ""
echo "--- Config checks ---"
for p in "${profiles[@]}"; do
  cfg="$HERMES_PROFILES_DIR/$p/config.yaml"
  if [[ ! -f "$cfg" ]]; then warn "$p: config.yaml missing"; continue; fi

  if grep -q "shared-skills\|\.hermes/skills" "$cfg" 2>/dev/null; then
    warn "$p: config.yaml references global shared-skills (should point to repo)"
  else
    ok "$p: config.yaml uses repo-local paths"
  fi

  if grep -q "byterover" "$cfg" 2>/dev/null; then
    ok "$p: memory provider=byterover"
  else
    warn "$p: memory provider not byterover"
  fi

  if grep -q "api_key:" "$cfg" 2>/dev/null; then
    ok "$p: model api_key configured"
  else
    warn "$p: model api_key missing"
  fi

  if python3 - "$cfg" <<'PY'
import sys, yaml
with open(sys.argv[1]) as f:
    config = yaml.safe_load(f) or {}
server = config.get("mcp_servers", {}).get("codegraph", {})
assert server.get("command") == "codegraph"
assert server.get("args") == ["serve", "--mcp"]
assert "mcp-codegraph" in config.get("platform_toolsets", {}).get("cli", [])
PY
  then
    ok "$p: CodeGraph MCP configured"
    if command -v codegraph >/dev/null 2>&1; then
      if hermes -p "$p" mcp test codegraph >/dev/null 2>&1; then
        ok "$p: CodeGraph MCP connected"
      else
        warn "$p: CodeGraph MCP connection failed"
      fi
    else
      recommend "$p: CodeGraph CLI not installed (recommended, optional)"
    fi
  else
    recommend "$p: CodeGraph MCP not configured (recommended, optional)"
  fi
done

# === 5. Skills loaded ===
echo ""
echo "--- Skills availability ---"
for p in "${profiles[@]}"; do
  count=$(hermes -p "$p" skills list 2>/dev/null | grep -c "enabled" || true)
  count="${count:-0}"
  if [[ "$count" -gt 0 ]]; then ok "$p: $count skills enabled"; else warn "$p: 0 skills enabled"; fi
done

# === 6. Bundled skills opt-out ===
echo ""
echo "--- Bundled skills opt-out ---"
for p in "${profiles[@]}"; do
  marker="$HERMES_PROFILES_DIR/$p/.no-bundled-skills"
  if [[ -f "$marker" ]]; then ok "$p: .no-bundled-skills present"; else warn "$p: .no-bundled-skills missing"; fi
done

# === 7. Workflow harness ===
echo ""
echo "--- Workflow harness ---"
ginflow="$ROOT/skills/ginflow/SKILL.md"
handoff="$ROOT/skills/ginflow/templates/session-handoff.md"
agents_template="$ROOT/templates/AGENTS.md"

for profile in gintary ginb; do
  if grep -q 'load and follow `ginflow`' "$ROOT/profiles/$profile.SOUL.md"; then
    ok "$profile: routes target-project work through ginflow"
  else
    warn "$profile: missing mandatory ginflow routing"
  fi
  ginflow_link="$HERMES_PROFILES_DIR/$profile/skills/ginflow"
  if [[ -L "$ginflow_link" && "$(readlink -f "$ginflow_link")" == "$ROOT/skills/ginflow" ]]; then
    ok "$profile: ginflow skill symlinked to canonical source"
  else
    warn "$profile: canonical ginflow skill symlink missing"
  fi
done

for heading in "Project session startup" "Execution contract" "Definition of done" "Session close and restart" "Optional session handoff export"; do
  if grep -q "^## $heading$" "$ginflow"; then ok "ginflow: $heading"; else warn "ginflow: missing $heading"; fi
done

for heading in "Ownership" "Work Artifacts" "Progress" "Verification Evidence" "Next Step" "Related Cards"; do
  if grep -q "^## $heading$" "$handoff"; then ok "handoff template: $heading"; else warn "handoff template: missing $heading"; fi
done

if grep -q 'Ask Gin which Kanban card to export' "$ginflow"; then ok "handoff export: Gin selects card"; else warn "handoff export: card selection rule missing"; fi
if grep -q 'Write only after approval' "$ginflow"; then ok "handoff export: write approval required"; else warn "handoff export: write approval rule missing"; fi
if grep -q 'Never mutate card status' "$ginflow"; then ok "handoff export: Kanban mutation forbidden"; else warn "handoff export: Kanban mutation guard missing"; fi
if grep -q 'come from `ginflow`' "$agents_template"; then ok "AGENTS template: routes shared workflow to ginflow"; else warn "AGENTS template: ginflow routing missing"; fi

if python3 "$ROOT/skills/ginflow/scripts/validate-harness.py" --setup-repo "$ROOT" >/dev/null; then
  ok "ginflow: five-subsystem static validation passed"
else
  warn "ginflow: five-subsystem static validation failed"
fi

# === 8. Repo drift ===
echo ""
echo "--- Repo drift ---"
mapfile -t drift_files < <(cd "$ROOT" && git status --porcelain --untracked-files=all 2>/dev/null | sed 's/^...//' | grep -E "^(profiles/|config/|scripts/|skills/|templates/|README\.md$|INSTALL\.md$)" || true)
if [[ "${#drift_files[@]}" -gt 0 ]]; then
  if [[ "$STRICT" == "1" ]]; then
    warn "Uncommitted canonical setup changes detected"
  else
    recommend "Uncommitted canonical setup changes detected (non-fatal)"
  fi
  printf '  %s\n' "${drift_files[@]:0:20}"
  [[ "${#drift_files[@]}" -gt 20 ]] && info "$(( ${#drift_files[@]} - 20 )) more files"
else
  ok "No uncommitted changes to canonical setup files"
fi

echo ""
if [[ "$FAILED" -eq 0 ]]; then ok "All checks passed."; else printf '⚠️  Some checks failed.\n' >&2; fi
exit "$FAILED"
