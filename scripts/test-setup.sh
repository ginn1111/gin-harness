#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/bin" "$TMP/home/.hermes/profiles/gintary" "$TMP/home/.hermes/profiles/ginb"
printf '{}\n' > "$TMP/home/.hermes/profiles/gintary/config.yaml"
printf '{}\n' > "$TMP/home/.hermes/profiles/ginb/config.yaml"
cat > "$TMP/bin/hermes" <<'EOF'
#!/usr/bin/env bash
printf 'Profile  Model\n ◆gintary  model\n  ginb  model\n'
EOF
chmod +x "$TMP/bin/hermes"

output="$(HERMES_REAL_HOME="$TMP/home" PATH="$TMP/bin:$PATH" make -s -C "$ROOT" setup)"
grep -q 'Integrating gintary' <<<"$output"
grep -q 'Integrating ginb' <<<"$output"
grep -q 'Dry-run complete' <<<"$output"
printf 'setup pinned-profile test ok\n'