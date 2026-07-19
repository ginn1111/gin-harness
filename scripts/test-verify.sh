#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${HERMES_TEST_PROFILE:-default}"

output=$(mktemp)
trap 'rm -f "$output"' EXIT

if ! "$ROOT/scripts/verify.sh" "$PROFILE" >"$output" 2>&1; then
  printf 'default verification must not fail only because repo is dirty\n' >&2
  cat "$output" >&2
  exit 1
fi

grep -q 'Uncommitted canonical integration changes detected (non-fatal)' "$output"

if "$ROOT/scripts/verify.sh" --strict "$PROFILE" >"$output" 2>&1; then
  printf 'strict verification must fail when canonical setup files are dirty\n' >&2
  cat "$output" >&2
  exit 1
fi

grep -q 'Uncommitted canonical integration changes detected' "$output"
printf 'verify behavior ok\n'
