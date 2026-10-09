#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HOME_ROOT="$TMP/home"
PROFILES="$HOME_ROOT/.hermes/profiles"
mkdir -p "$PROFILES/alpha/plugins"
printf 'skills:\n  external_dirs:\n    - keep-me\nplugins:\n  enabled:\n    - keep-plugin\n' > "$PROFILES/alpha/config.yaml"

export HERMES_REAL_HOME="$HOME_ROOT"
export HERMES_PROFILES_DIR="$PROFILES"
export GINFLOW_INSTALL_MANIFEST="$TMP/.ginflow-install.json"

bash "$ROOT/scripts/install.sh" install alpha
[[ -f "$PROFILES/alpha/skills/ginflow/SKILL.md" ]]
[[ -f "$PROFILES/alpha/skills/ginflow/lib/harness_core.py" ]]
[[ -f "$PROFILES/alpha/plugins/with-chatgpt/plugin.yaml" ]]
[[ -f "$PROFILES/alpha/plugins/with-chatgpt/__init__.py" ]]
[[ ! -e "$HOME_ROOT/.agents/skills/ginflow" ]]
[[ -f "$GINFLOW_INSTALL_MANIFEST" ]]

python3 - "$PROFILES/alpha/config.yaml" <<'PY'
import sys
from pathlib import Path
text = Path(sys.argv[1]).read_text()
assert "keep-me" in text
assert "keep-plugin" in text
PY

bash "$ROOT/scripts/install.sh" install alpha >/dev/null
[[ -f "$PROFILES/alpha/skills/ginflow/SKILL.md" ]]
[[ ! -e "$HOME_ROOT/.agents/skills/ginflow" ]]

bash "$ROOT/scripts/install.sh" uninstall
[[ ! -e "$PROFILES/alpha/skills/ginflow" ]]
[[ -f "$PROFILES/alpha/config.yaml" ]]
[[ ! -e "$GINFLOW_INSTALL_MANIFEST" ]]

# Failure mid-install restores every prior path; conflicts and profile state survive.
if [[ "$(id -u)" != "0" ]]; then
  A="$PROFILES/alpha"
  mkdir -p "$A/skills/ginflow" "$A/plugins/with-chatgpt" "$A/sessions" "$A/memories" "$PROFILES/beta/plugins"
  printf 'prior-skill\n' > "$A/skills/ginflow/prior.txt"
  printf 'prior-plugin\n' > "$A/plugins/with-chatgpt/prior.txt"
  printf 'secret\n' > "$A/.env"
  printf 'auth\n' > "$A/auth.json"
  printf 'session\n' > "$A/sessions/s.txt"
  printf 'memory\n' > "$A/memories/m.md"
  cp "$A/config.yaml" "$PROFILES/beta/config.yaml"
  chmod 555 "$PROFILES/beta/plugins"
  if bash "$ROOT/scripts/install.sh" install alpha beta >/dev/null 2>&1; then
    chmod 755 "$PROFILES/beta/plugins"
    echo "expected install failure" >&2
    exit 1
  fi
  chmod 755 "$PROFILES/beta/plugins"
  [[ ! -e "$GINFLOW_INSTALL_MANIFEST" ]]
  [[ "$(cat "$A/skills/ginflow/prior.txt")" == "prior-skill" ]]
  [[ "$(cat "$A/plugins/with-chatgpt/prior.txt")" == "prior-plugin" ]]
  [[ ! -e "$A/skills/ginflow/SKILL.md" && ! -e "$A/plugins/with-chatgpt/plugin.yaml" ]]
  [[ ! -e "$PROFILES/beta/skills/ginflow" && ! -e "$PROFILES/beta/plugins/with-chatgpt" ]]
  [[ -z "$(find "$PROFILES" -name '*.bak.ginflow-install')" ]]

  bash "$ROOT/scripts/install.sh" install alpha >/dev/null
  [[ -f "$A/plugins/with-chatgpt/plugin.yaml" ]]
  printf 'local edit\n' > "$A/plugins/with-chatgpt/extra.txt"
  if bash "$ROOT/scripts/install.sh" uninstall >/dev/null 2>&1; then
    echo "expected uninstall conflict" >&2
    exit 1
  fi
  [[ -f "$A/plugins/with-chatgpt/extra.txt" && -f "$GINFLOW_INSTALL_MANIFEST" ]]
  rm "$A/plugins/with-chatgpt/extra.txt"
  bash "$ROOT/scripts/install.sh" uninstall >/dev/null
  [[ "$(cat "$A/skills/ginflow/prior.txt")" == "prior-skill" ]]
  [[ "$(cat "$A/plugins/with-chatgpt/prior.txt")" == "prior-plugin" ]]
  [[ "$(cat "$A/.env")" == "secret" && "$(cat "$A/auth.json")" == "auth" ]]
  [[ "$(cat "$A/sessions/s.txt")" == "session" && "$(cat "$A/memories/m.md")" == "memory" ]]
fi

echo "install/uninstall tests passed"
