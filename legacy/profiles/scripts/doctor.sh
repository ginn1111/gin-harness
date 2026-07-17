#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- helpers ---
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; BLD='\033[1m'; NC='\033[0m'
fail=0
pass() { printf "${GRN}✓${NC} %s\n" "$1"; }
warn() { printf "${YLW}⚠ %s${NC}\n" "$1"; fail=1; }
failf() { printf "${RED}✗ %s${NC}\n" "$1"; fail=1; }
section() { printf "\n${BLD}%s${NC}\n" "$1"; }

# Resolve real user home — Hermes sessions may override $HOME to profile-local
realhome() {
  local h
  h=$(getent passwd "$(whoami)" 2>/dev/null | cut -d: -f6)
  echo "${h:-$HOME}"
}
RH=$(realhome)

# --- 1. Hermes itself ---
section "Hermes CLI"
if command -v hermes >/dev/null 2>&1; then
  v=$(hermes --version 2>/dev/null || hermes -v 2>/dev/null || echo "installed")
  pass "hermes found ($v)"
else
  failf "hermes not in PATH. Install: pip install hermes-agent"
fi

# --- 2. Runtime deps ---
section "Runtime dependencies"
for cmd in python3 git node; do
  command -v "$cmd" >/dev/null 2>&1 && pass "$cmd found" || failf "$cmd missing"
done
python3 -c "import yaml" 2>/dev/null && pass "PyYAML available" || warn "PyYAML missing (pip install -r requirements.txt)"
node -e "require('child_process')" 2>/dev/null && pass "node works" || failf "node broken"

# --- 3. Profile existence ---
section "Delivery profiles"
declare -A roles=(
  [ginb]="builder"
  [ginr]="reviewer"
  [gins]="shipper"
  [gino]="orchestrator"
)
existing=$(hermes profile list 2>/dev/null || true)
for p in "${!roles[@]}"; do
  if grep -Eq "(^|[[:space:]])${p}([[:space:]]|$)" <<<"$existing"; then
    dir="$RH/.hermes/profiles/$p"
    ok=true
    [[ -f "$dir/SOUL.md" ]] || { warn "$p: missing SOUL.md"; ok=false; }
    [[ -f "$dir/.no-bundled-skills" ]] || { warn "$p: missing .no-bundled-skills"; ok=false; }
    "$ok" && pass "$p (${roles[$p]}) ✓" || warn "$p (${roles[$p]}) — partial"
  else
    warn "$p (${roles[$p]}) — not created"
  fi
done

# --- 4. Shared skills ---
section "Shared skills"
if [[ -d "$RH/.hermes/shared-skills/mattpocock-skills/.git" ]]; then
  pass "Matt Pocock skills repository"
else
  warn "Matt Pocock skills not cloned"
fi
if [[ -d "$RH/.hermes/shared-skills/byterover" ]]; then
  pass "ByteRover skill present"
else
  warn "ByteRover skill missing"
fi
if [[ -d "$RH/.hermes/shared-skills" ]]; then
  pass "shared-skills directory exists"
fi

# --- 5. Byterover ---
section "ByteRover"
brv_auth="$RH/.hermes/shared-skills/byterover/scripts/auth.mjs"
if [[ -f "$brv_auth" ]] && node "$brv_auth" whoami 2>/dev/null | grep -q '"authed":true'; then
  pass "ByteRover authenticated"
else
  warn "ByteRover not authenticated (run: node scripts/auth.mjs)"
fi
brv_space="$RH/.hermes/shared-skills/byterover/scripts/space.mjs"
if [[ -f "$brv_space" ]]; then
  # Check from a known-bound directory (gintary profile home)
  bound_dir="$RH/.hermes/profiles/gintary"
  if [[ -d "$bound_dir" ]]; then
    space_json=$(cd "$bound_dir" && node "$brv_space" current 2>/dev/null || echo '{"ok":false}')
  else
    space_json=$(node "$brv_space" current 2>/dev/null || echo '{"ok":false}')
  fi
  if echo "$space_json" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('ok') else 1)" 2>/dev/null; then
    pass "ByteRover space bound ($(echo "$space_json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['space_name'])" 2>/dev/null))"
  else
    warn "ByteRover space not bound (run space bind from gintary profile)"
  fi
fi

# --- 6. Tool proposals vs reality ---
section "Toolset proposals"
for p in ginb ginr gins gino; do
  if [[ -f "$ROOT/toolsets/$p.yaml" ]]; then
    pass "$p: proposal exists"
  else
    warn "$p: no proposal file"
  fi
done

# --- summary ---
section "Summary"
if [[ "$fail" -eq 0 ]]; then
  printf "${GRN}All checks passed. Ready to provision.${NC}\n"
else
  printf "${YLW}Some items need attention.${NC}\n"
fi
exit "$fail"
