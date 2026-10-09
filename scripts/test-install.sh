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

echo "install/uninstall tests passed"
