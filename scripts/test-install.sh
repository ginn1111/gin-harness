#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HOME_ROOT="$TMP/home"
PROFILES="$HOME_ROOT/.hermes/profiles"
FAKE_BIN="$TMP/bin"
mkdir -p "$FAKE_BIN" "$PROFILES/alpha/plugins" "$PROFILES/beta/plugins"
for profile in alpha beta; do
  cat > "$PROFILES/$profile/config.yaml" <<'YAML'
skills:
  external_dirs: []
plugins:
  enabled: []
custom:
  keep: true
YAML
done
ln -s "$ROOT/plugins/ginflow-gate" "$PROFILES/beta/plugins/ginflow-gate"
cat > "$FAKE_BIN/hermes" <<'SH'
#!/usr/bin/env bash
if [[ "${1:-}" == "profile" && "${2:-}" == "list" ]]; then
  printf 'Profile Model Gateway\n default aux running\n alpha coder running\n beta aux stopped\n'
  exit 0
fi
exit 1
SH
chmod +x "$FAKE_BIN/hermes"

export PATH="$FAKE_BIN:$PATH"
export HERMES_REAL_HOME="$HOME_ROOT"
export HERMES_PROFILES_DIR="$PROFILES"

assert_file() { [[ -e "$1" ]] || { echo "missing: $1" >&2; exit 1; }; }

bash "$ROOT/scripts/install.sh" install
assert_file "$HOME_ROOT/.agent/skills/ginflow/SKILL.md"
assert_file "$PROFILES/alpha/plugins/ginflow-gate/plugin.yaml"
assert_file "$PROFILES/beta/plugins/ginflow-gate/plugin.yaml"
assert_file "$ROOT/.ginflow-install.json"
python3 - "$PROFILES/alpha/config.yaml" <<'PY'
import sys, yaml
config = yaml.safe_load(open(sys.argv[1]))
assert "ginflow-gate" in config["plugins"]["enabled"]
assert config["custom"]["keep"] is True
PY

# Reinstall is idempotent and must not duplicate config entries.
bash "$ROOT/scripts/install.sh" install >/dev/null
python3 - "$PROFILES/alpha/config.yaml" <<'PY'
import sys, yaml
config = yaml.safe_load(open(sys.argv[1]))
assert config["plugins"]["enabled"].count("ginflow-gate") == 1
assert config["skills"]["external_dirs"].count(config["skills"]["external_dirs"][0]) == 1
PY

# User edits are protected during uninstall.
printf '\n# user edit\n' >> "$PROFILES/alpha/plugins/ginflow-gate/plugin.yaml"
if bash "$ROOT/scripts/install.sh" uninstall >/dev/null 2>&1; then
  echo "uninstall should report changed plugin conflict" >&2
  exit 1
fi
assert_file "$PROFILES/alpha/plugins/ginflow-gate/plugin.yaml"
assert_file "$ROOT/.ginflow-install.json"

# Restore the managed copy, then uninstall cleanly.
rm -rf "$PROFILES/alpha/plugins/ginflow-gate"
cp -R "$ROOT/plugins/ginflow-gate" "$PROFILES/alpha/plugins/ginflow-gate"
bash "$ROOT/scripts/install.sh" uninstall
[[ ! -e "$HOME_ROOT/.agent/skills/ginflow" ]]
[[ ! -e "$PROFILES/alpha/plugins/ginflow-gate" ]]
[[ -L "$PROFILES/beta/plugins/ginflow-gate" ]]
[[ "$(readlink "$PROFILES/beta/plugins/ginflow-gate")" == "$ROOT/plugins/ginflow-gate" ]]
[[ ! -e "$ROOT/.ginflow-install.json" ]]

echo "install/uninstall tests passed"
