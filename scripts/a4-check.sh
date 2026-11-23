#!/bin/bash

# Ensure the adhocracy4 commit locked for Python (uv.lock) and JavaScript
# (pnpm-lock.yaml) is the same, so backend and frontend come from one a4 commit.
set -e

UV_LOCK_FILE="uv.lock"
PNPM_LOCK_FILE="pnpm-lock.yaml"

UV_HASH=$(grep -o 'liqd/adhocracy4\.git?[^#"]*#[0-9a-f]\{40\}' "$UV_LOCK_FILE" | head -n1 | sed 's/.*#//')
PNPM_HASH=$(grep -o 'codeload\.github\.com/liqd/adhocracy4/tar\.gz/[0-9a-f]\{40\}' "$PNPM_LOCK_FILE" | head -n1 | sed 's|.*/||')

if [[ -z "$UV_HASH" ]]; then
  echo "Could not find the adhocracy4 commit in $UV_LOCK_FILE." >&2
  exit 1
fi

if [[ -z "$PNPM_HASH" ]]; then
  echo "Could not find the adhocracy4 commit in $PNPM_LOCK_FILE." >&2
  exit 1
fi

if [[ "$UV_HASH" != "$PNPM_HASH" ]]; then
  echo "adhocracy4 commit mismatch:" >&2
  echo "  $UV_LOCK_FILE: $UV_HASH" >&2
  echo "  $PNPM_LOCK_FILE: $PNPM_HASH" >&2
  echo "Run 'make bump-a4' to update both." >&2
  exit 1
fi

echo "OK: adhocracy4 $UV_HASH matches in $UV_LOCK_FILE and $PNPM_LOCK_FILE."
