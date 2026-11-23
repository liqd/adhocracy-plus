#!/bin/bash

# Ensure the pinned Playwright version in pyproject.toml matches the tag of the
# official Playwright Docker image used by the e2e CI job, so the installed
# playwright package always finds matching browser binaries.
set -e

PYPROJECT_FILE="pyproject.toml"
WORKFLOW_FILE=".github/workflows/django.yml"

PLAYWRIGHT_VERSION=$(sed -n 's/^[[:space:]]*"playwright==\([^"]*\)",\{0,1\}$/\1/p' "$PYPROJECT_FILE")
IMAGE_TAG=$(grep -E 'container: mcr\.microsoft\.com/playwright/python' "$WORKFLOW_FILE" | sed 's/.*python:v\(.*\)-noble.*/\1/')

if [[ $(printf '%s\n' "$PLAYWRIGHT_VERSION" | grep -c .) -ne 1 ]]; then
  echo "Could not find exactly one pinned 'playwright==<version>' in $PYPROJECT_FILE." >&2
  exit 1
fi

if [[ -z "$IMAGE_TAG" ]]; then
  echo "Could not find a 'container: mcr.microsoft.com/playwright/python:v<version>-noble' in $WORKFLOW_FILE." >&2
  exit 1
fi

if [[ "$PLAYWRIGHT_VERSION" != "$IMAGE_TAG" ]]; then
  echo "Playwright version mismatch:" >&2
  echo "  $PYPROJECT_FILE pins playwright==$PLAYWRIGHT_VERSION" >&2
  echo "  $WORKFLOW_FILE uses container tag v$IMAGE_TAG-noble" >&2
  echo "Bump the e2e container tag in $WORKFLOW_FILE to v$PLAYWRIGHT_VERSION-noble (or pin playwright in $PYPROJECT_FILE to $IMAGE_TAG)." >&2
  exit 1
fi

echo "OK: playwright==$PLAYWRIGHT_VERSION matches e2e container tag v$IMAGE_TAG-noble."
