#!/usr/bin/env bash
# Bootstrap: curl -fsSL https://raw.githubusercontent.com/ginn1111/gin-harness/main/install.sh | bash
# Env: GIN_HARNESS_DIR (default ~/.gin-harness), GIN_HARNESS_REF (default main),
#      GIN_HARNESS_REPO, PROFILES="a b" (default: every Hermes profile with a config.yaml).
set -euo pipefail

REPO="${GIN_HARNESS_REPO:-https://github.com/ginn1111/gin-harness.git}"
DIR="${GIN_HARNESS_DIR:-$HOME/.gin-harness}"
REF="${GIN_HARNESS_REF:-main}"

die() { printf '❌ %s\n' "$*" >&2; exit 1; }
for tool in git python3 make; do command -v "$tool" >/dev/null || die "missing: $tool"; done
command -v hermes >/dev/null || printf '⚠️  hermes not found; install it first (see README), profiles are required\n' >&2

if [[ -d "$DIR/.git" ]]; then
  [[ -z "$(git -C "$DIR" status --porcelain)" ]] || die "$DIR has local changes; commit or stash them first"
elif [[ -e "$DIR" && -n "$(ls -A "$DIR" 2>/dev/null)" ]]; then
  die "$DIR exists and is not a gin-harness clone"
else
  git clone --quiet "$REPO" "$DIR"
fi
git -C "$DIR" fetch --quiet origin "$REF"
git -C "$DIR" checkout --quiet FETCH_HEAD

profiles_dir="${HERMES_PROFILES_DIR:-${HERMES_REAL_HOME:-$HOME}/.hermes/profiles}"
if [[ -n "${PROFILES:-}" ]]; then
  targets="$PROFILES"
else
  targets="$(for c in "$profiles_dir"/*/config.yaml; do [[ -f "$c" ]] && basename "$(dirname "$c")"; done | tr '\n' ' ')"
fi
printf 'ℹ️  installing Ginflow into profiles: %s\n' "${targets:-none found}"

make -C "$DIR" doctor
make -C "$DIR" install PROFILES="${PROFILES:-}"
printf '\n✅ done. Next: hermes plugins enable ginflow-gate, then restart Hermes sessions.\n'
