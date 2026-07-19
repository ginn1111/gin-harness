#!/usr/bin/env bash
set -euo pipefail
# Plug setup-repo integrations into existing Hermes-native profiles.
# Usage: ./scripts/setup.sh [--apply] <profile> [profile ...]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APPLY=0
if [[ "${1:-}" == "--apply" ]]; then APPLY=1; shift; fi
[[ "$#" -gt 0 ]] || { printf 'Usage: %s [--apply] <profile> [profile ...]\n' "$0" >&2; exit 2; }

info() { printf 'ℹ️  %s\n' "$*"; }
ok() { printf '✅ %s\n' "$*"; }
die() { printf '❌ %s\n' "$*" >&2; exit 1; }
command -v hermes >/dev/null || die "Missing: hermes"
command -v python3 >/dev/null || die "Missing: python3"

REAL_HOME="$(getent passwd "$(whoami)" 2>/dev/null | cut -d: -f6)"
REAL_HOME="${REAL_HOME:-$HOME}"
PROFILES_DIR="$REAL_HOME/.hermes/profiles"
export HOME="$REAL_HOME"
unset HERMES_HOME

existing="$(hermes profile list 2>/dev/null || true)"
for profile in "$@"; do
  [[ "$profile" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || die "$profile: invalid profile name"
  grep -qw "$profile" <<<"$existing" || die "$profile: profile missing; install it first with 'hermes profile install <distribution> --name $profile'"
  profile_dir="$PROFILES_DIR/$profile"
  config="$profile_dir/config.yaml"
  [[ -f "$config" ]] || die "$profile: native config missing at $config"

  echo
  info "Integrating $profile (SOUL.md and distribution.yaml remain profile-owned)"
  if [[ "$APPLY" == 0 ]]; then
    info "$profile: would link skills/ginflow and plugins/herdr-agent-state"
    info "$profile: would add repo skill dirs, CodeGraph MCP, toolsets, and plugin enablement to native config"
    continue
  fi

  mkdir -p "$profile_dir/skills" "$profile_dir/plugins"
  for link in "$profile_dir/skills/ginflow" "$profile_dir/plugins/herdr-agent-state"; do
    if [[ -e "$link" && ! -L "$link" ]]; then
      backup="$link.bak.integration.$(date +%s)"
      mv "$link" "$backup"
      info "$profile: backed up $(basename "$link") to $backup"
    fi
  done
  ln -sfnT "$ROOT/skills/ginflow" "$profile_dir/skills/ginflow"
  ln -sfnT "$ROOT/plugins/herdr-agent-state" "$profile_dir/plugins/herdr-agent-state"

  python3 - "$config" "$ROOT" <<'PY'
import sys
from pathlib import Path
import yaml
path, root = Path(sys.argv[1]), Path(sys.argv[2])
config = yaml.safe_load(path.read_text()) or {}
external = config.setdefault("skills", {}).setdefault("external_dirs", [])
for candidate in (str(root / "skills"), str(root / "community/mattpocock-skills/skills")):
    if Path(candidate).is_dir() and candidate not in external:
        external.append(candidate)
cli = config.setdefault("platform_toolsets", {}).setdefault("cli", [])
for toolset in ("code_execution", "delegation", "file", "kanban", "memory", "session_search", "skills", "terminal", "todo", "vision", "web", "mcp-codegraph"):
    if toolset not in cli:
        cli.append(toolset)
config.setdefault("mcp_servers", {})["codegraph"] = {
    "command": "codegraph", "args": ["serve", "--mcp"],
    "timeout": 120, "connect_timeout": 60, "enabled": True,
}
enabled = config.setdefault("plugins", {}).setdefault("enabled", [])
if "herdr-agent-state" not in enabled:
    enabled.append("herdr-agent-state")
backup = path.with_name(path.name + ".bak.integration")
if not backup.exists():
    backup.write_text(path.read_text())
path.write_text(yaml.safe_dump(config, sort_keys=False))
PY
  ok "$profile: integrations applied; native identity and distribution untouched"
done

if [[ "$APPLY" == 1 ]]; then
  echo
  ok "Integration complete. Restart profile sessions, then run: ./scripts/verify.sh $*"
else
  echo
  info "Dry-run complete. Re-run with --apply."
fi
