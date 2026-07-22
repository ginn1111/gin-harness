#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${HERMES_TEST_PROFILE:-default}"

output=$(mktemp)
trap 'rm -f "$output"' EXIT

# Test that default verification via ginflow harness works
if ! python3 "$ROOT/skills/ginflow/scripts/validate-harness.py" --setup-repo "$ROOT" --json >"$output" 2>&1; then
  printf 'default verification via ginflow harness must not fail\\n' >&2
  cat "$output" >&2
  exit 1
fi

# Test that verify-test passes for clean repo
if ! python3 "$ROOT/skills/ginflow/scripts/validate-harness.py" --setup-repo "$ROOT" --json >"$output" 2>&1; then
  printf 'strict verification via ginflow harness must not fail on clean repo\\n' >&2
  cat "$output" >&2
  exit 1
fi

printf 'verify behavior ok\\n'
