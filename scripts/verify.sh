#!/usr/bin/env bash
set -euo pipefail
# verify.sh — Verify delivery profiles match repo templates.
# Reports any drift between deployed config and repo source of truth.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FAILED=0

info()  { printf 'ℹ️  %s\n' "$*"; }
ok()    { printf '✅ %s\n' "$*"; }
warn()  { printf '⚠️  %s\n' "$*" >&2; FAILED=1; }
die()   { printf '❌ %s\n' "$*" >&2; exit 1; }
require_command() { command -v "$1" >/dev/null 2>&1 || die "Missing: $1"; }
require_command hermes

# Resolve real user home (profile sessions may override $HOME)
REAL_HOME="$(getent passwd "$(whoami)" 2>/dev/null | cut -d: -f6)"
REAL_HOME="${REAL_HOME:-$HOME}"
HERMES_PROFILES_DIR="$REAL_HOME/.hermes/profiles"

profiles=(ginb ginr gins gino)

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

# === 6. Git diff ===
echo ""
echo "--- Repo drift ---"
if cd "$ROOT" && git diff --name-only 2>/dev/null | grep -qE "^(profiles/|config/|scripts/)"; then
  warn "Uncommitted changes to canonical files detected"
  cd "$ROOT" && git diff --stat 2>/dev/null | head -20
else
  ok "No uncommitted changes to canonical files"
fi

# === Summary ===
echo ""
if [[ "$FAILED" -eq 0 ]]; then ok "All checks passed."; else warn "Some checks failed."; fi
exit "$FAILED"
