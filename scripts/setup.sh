#!/usr/bin/env bash
set -euo pipefail
# setup.sh — Bootstrap delivery profiles from repo templates.
#
# Usage: ./scripts/setup.sh [--apply]
#
# Reads:   config/profiles.yaml, config/profile.yaml.tmpl, profiles/*.SOUL.md
# Requires: .env in repo root with GIN_API_KEY, GIN_BASE_URL, GIN_HOST
# Requires: hermes CLI, python3 (PyYAML)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

info()  { printf 'ℹ️  %s\n' "$*"; }
ok()    { printf '✅ %s\n' "$*"; }
warn()  { printf '⚠️  %s\n' "$*" >&2; }
die()   { printf '❌ %s\n' "$*" >&2; exit 1; }
run_or_print() {
  if [[ "$APPLY" == "1" ]]; then "$@"; else printf '[dry-run] %q\n' "$*"; fi
}
require_command() { command -v "$1" >/dev/null 2>&1 || die "Missing: $1"; }
require_command hermes

# Resolve real user home (profile sessions may override $HOME)
REAL_HOME="$(getent passwd "$(whoami)" 2>/dev/null | cut -d: -f6)"
REAL_HOME="${REAL_HOME:-$HOME}"
HERMES_PROFILES_DIR="$REAL_HOME/.hermes/profiles"
require_command python3

# === load config ===
PROFILES_YAML="$ROOT/config/profiles.yaml"
TEMPLATE="$ROOT/config/profile.yaml.tmpl"
[[ -f "$PROFILES_YAML" ]] || die "Missing $PROFILES_YAML"
[[ -f "$TEMPLATE" ]]      || die "Missing $TEMPLATE"

# === load .env if present ===
[[ -f "$ROOT/.env" ]] && set -a && source "$ROOT/.env" && set +a
GIN_API_KEY="${GIN_API_KEY:-}"
GIN_BASE_URL="${GIN_BASE_URL:-https://agents.gin1111.dev/v1}"
GIN_HOST="${GIN_HOST:-agents.gin1111.dev}"
info "GIN_BASE_URL=$GIN_BASE_URL  GIN_HOST=$GIN_HOST"
[[ -z "$GIN_API_KEY" ]] && warn "GIN_API_KEY not set — auth will fail"

# === detect community skills dir ===
COMMUNITY_SKILLS_DIR=""
for d in "$ROOT/community/mattpocock-skills/skills" "$ROOT/.hermes/shared-skills/mattpocock-skills/skills"; do
  [[ -d "$d" ]] && { COMMUNITY_SKILLS_DIR="$d"; break; }
done
CUSTOM_SKILLS_DIR="$ROOT/skills"
[[ -d "$CUSTOM_SKILLS_DIR" ]] || CUSTOM_SKILLS_DIR=""

# === parse profiles.yaml into arrays ===
declare -a NAMES DESCS SKINS
while IFS='|' read -r name desc skin; do
  NAMES+=("$name")
  DESCS+=("$desc")
  SKINS+=("$skin")
done < <(python3 -c "
import yaml, sys
with open('$PROFILES_YAML') as f:
    data = yaml.safe_load(f)
for name, cfg in data.get('profiles', {}).items():
    skin = cfg.get('display_skin', 'default')
    desc = cfg.get('description', '').replace('|', '/')
    print(f'{name}|{desc}|{skin}')
")

# === main loop ===
for i in "${!NAMES[@]}"; do
  name="${NAMES[$i]}"
  desc="${DESCS[$i]}"
  skin="${SKINS[$i]}"
  echo ""
  info "Processing $name"

  profile_dir="$HERMES_PROFILES_DIR/$name"
  config_file="$profile_dir/config.yaml"
  soul_link="$profile_dir/SOUL.md"
  source_soul="$ROOT/profiles/$name.SOUL.md"

  # 1. Create profile if missing
  if hermes profile list 2>/dev/null | grep -qw "$name"; then
    ok "$name: profile exists"
  else
    info "$name: creating..."
    run_or_print hermes profile create "$name" --no-skills --description "$desc"
  fi

  # 2. Symlink SOUL.md
  if [[ -f "$source_soul" ]]; then
    if [[ "$APPLY" == "1" ]]; then
      [[ -f "$soul_link" && ! -L "$soul_link" ]] && cp "$soul_link" "$soul_link.bak.$(date +%s)" && info "  backed up old SOUL.md"
      ln -sf "$source_soul" "$soul_link"
      ok "$name: SOUL.md symlinked"
    else
      info "$name: would symlink SOUL.md → $source_soul"
    fi
  else
    warn "$name: SOUL.md source missing at $source_soul"
  fi

  # 3. Generate config.yaml
  if [[ "$APPLY" == "1" ]]; then
    mkdir -p "$profile_dir"
    [[ -f "$config_file" && ! -L "$config_file" ]] && cp "$config_file" "$config_file.bak.$(date +%s)" && info "  backed up config.yaml"
    sed \
      -e "s|{{PROFILE}}|$name|g" \
      -e "s|{{GIN_BASE_URL}}|$GIN_BASE_URL|g" \
      -e "s|{{GIN_HOST}}|$GIN_HOST|g" \
      -e "s|{{DISPLAY_SKIN}}|$skin|g" \
      -e "s|{{REPO_DIR}}|$ROOT|g" \
      "$TEMPLATE" > "$config_file"
    ok "$name: config.yaml generated"
  else
    info "$name: would generate config.yaml from template"
  fi

  # 4. Warn about missing external_dirs
  if [[ "$APPLY" == "1" ]]; then
    for d in "$CUSTOM_SKILLS_DIR" "$COMMUNITY_SKILLS_DIR"; do
      [[ -n "$d" && ! -d "$d" ]] && warn "$name: external_dir $d not found (silently skipped by Hermes)"
    done
  fi
done

# === summary ===
echo ""
if [[ "$APPLY" == "1" ]]; then
  ok "Setup complete. Next:"
  echo "  1. cp .env → ~/.hermes/profiles/<name>/.env  (API keys)"
  echo "  2. Run: ./scripts/verify.sh"
else
  info "Dry-run complete. Run with --apply to execute."
fi
