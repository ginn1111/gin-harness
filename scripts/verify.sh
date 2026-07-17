#!/usr/bin/env bash
set -euo pipefail
# verify.sh — Verify delivery profiles match repo templates + hybrid kanban/markdown drift.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FAILED=0

info()  { printf 'ℹ️  %s\n' "$*"; }
ok()    { printf '✅ %s\n' "$*"; }
warn()  { printf '⚠️  %s\n' "$*" >&2; FAILED=1; }
die()   { printf '❌ %s\n' "$*" >&2; exit 1; }
require_command() { command -v "$1" >/dev/null 2>&1 || die "Missing: $1"; }
require_command hermes

REAL_HOME="$(getent passwd "$(whoami)" 2>/dev/null | cut -d: -f6)"
REAL_HOME="${REAL_HOME:-$HOME}"
HERMES_PROFILES_DIR="$REAL_HOME/.hermes/profiles"

profiles=(gintary ginb)

echo "===== Delivery Profile Verification ====="

# === 1. Profile existence ===
echo ""
echo "--- Profile existence ---"
existing=$(hermes profile list 2>/dev/null || true)
for p in "${profiles[@]}"; do
  if grep -qw "$p" <<<"$existing"; then ok "$p: exists"; else warn "$p: NOT FOUND"; fi
done

# === 2. SOUL.md ===
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

# === 3. Config ===
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
done

# === 4. Skills loaded ===
echo ""
echo "--- Skills availability ---"
for p in "${profiles[@]}"; do
  count=$(hermes -p "$p" skills list 2>/dev/null | grep -c "enabled" || echo "0")
  if [[ "$count" -gt 0 ]]; then ok "$p: $count skills enabled"; else warn "$p: 0 skills enabled"; fi
done

# === 5. Bundled skills opt-out ===
echo ""
echo "--- Bundled skills opt-out ---"
for p in "${profiles[@]}"; do
  marker="$HERMES_PROFILES_DIR/$p/.no-bundled-skills"
  if [[ -f "$marker" ]]; then ok "$p: .no-bundled-skills present"; else warn "$p: .no-bundled-skills missing"; fi
done

# === 6. Repo drift ===
echo ""
echo "--- Repo drift ---"
if cd "$ROOT" && git diff --name-only 2>/dev/null | grep -qE "^(profiles/|config/|scripts/)"; then
  warn "Uncommitted changes to canonical files detected"
  cd "$ROOT" && git diff --stat 2>/dev/null | head -20
else
  ok "No uncommitted changes to canonical files"
fi

# === 7. Hybrid drift — kanban vs markdown ===
echo ""
echo "--- Kanban / Markdown drift ---"

# Extract YAML frontmatter value, strip inline comments
yaml_val() {
  local file="$1" key="$2"
  awk -v k="$key" '
    /^---$/ { if (count==0) {count=1; next} if (count==1) {count=2; exit} }
    count==1 && $0 ~ "^"k":" {
      sub(/^[^:]+:[[:space:]]*/,"")
      sub(/[[:space:]]*#.*$/,"")  # strip inline comments
      gsub(/^[[:space:]]+|[[:space:]]+$/,"")  # trim
      print
      exit
    }
  ' "$file"
}

drift_checked=0

for brief in "$ROOT"/briefs/DM-*.md; do
  [[ -f "$brief" ]] || continue

  kanban_id=$(yaml_val "$brief" "kanban")
  [[ -z "$kanban_id" ]] && continue
  [[ "$kanban_id" == "t_XXXX" ]] && continue

  md_status=$(yaml_val "$brief" "status")
  drift_checked=$((drift_checked + 1))

  # Write JSON to temp file to avoid shell quoting hell
  tmp=$(mktemp)
  hermes kanban show "$kanban_id" --json > "$tmp" 2>/dev/null || {
    warn "$(basename "$brief"): kanban task $kanban_id not found (stale ref?)"
    rm -f "$tmp"
    continue
  }

  # Parse via temp file
  kb_status=$(python3 -c "
import sys, json
with open('$tmp') as f:
    d = json.load(f)
    t = d.get('task', d)
    print(t.get('status', 'unknown') or 'unknown')
" 2>/dev/null || echo "unknown")

  md_sha_at_complete=$(python3 -c "
import sys, json
with open('$tmp') as f:
    d = json.load(f)
    t = d.get('task', d)
    m = t.get('metadata', {}) or {}
    print(m.get('md_sha_at_complete', '') or '')
" 2>/dev/null || echo "")

  md_sha_at_create=$(python3 -c "
import sys, json
with open('$tmp') as f:
    d = json.load(f)
    t = d.get('task', d)
    m = t.get('metadata', {}) or {}
    print(m.get('md_sha_at_create', '') or '')
" 2>/dev/null || echo "")

  rm -f "$tmp"

  current_sha=$(cd "$ROOT" && git rev-parse HEAD -- "$brief" 2>/dev/null || echo "no_git")

  # Status drift — skip running (ginb mid-work)
  if [[ "$kb_status" != "running" ]]; then
    if [[ "$kb_status" != "$md_status" ]]; then
      warn "$(basename "$brief"): STATUS DRIFT — kanban=$kb_status  markdown=$md_status"
    fi
  fi

  # Content drift — SHA mismatch after delivery closed
  if [[ -n "$md_sha_at_complete" ]] && [[ "$md_sha_at_complete" != "$current_sha" ]]; then
    warn "$(basename "$brief"): CONTENT DRIFT — changed after delivery closed"
    cd "$ROOT" && git diff --stat "$md_sha_at_complete"..HEAD -- "$brief" 2>/dev/null || true
    cd "$ROOT" && git diff "$md_sha_at_complete"..HEAD -- "$brief" 2>/dev/null | head -40 || true
  fi

  if [[ -z "$md_sha_at_complete" ]] && [[ -n "$md_sha_at_create" ]]; then
    info "$(basename "$brief"): kanban=$kb_status md=$md_status (no complete SHA yet)"
  fi
done

if [[ "$drift_checked" -eq 0 ]]; then
  info "No linked briefs to check."
else
  ok "Checked $drift_checked brief(s) for drift"
fi

echo ""
if [[ "$FAILED" -eq 0 ]]; then ok "All checks passed."; else warn "Some checks failed."; fi
exit "$FAILED"
