#!/bin/bash

# Ensure the pinned Playwright version in the pip requirements matches the tag
# of the official Playwright Docker image used by the e2e CI job, so the
# installed playwright package always finds matching browser binaries.
set -e

REQUIREMENTS_FILE="requirements/dev.txt"
WORKFLOW_FILE=".github/workflows/django.yml"

PLAYWRIGHT_VERSION=$(grep -E '^playwright==' "$REQUIREMENTS_FILE" | sed 's/.*==//')
IMAGE_TAG=$(grep -E 'container: mcr\.microsoft\.com/playwright/python' "$WORKFLOW_FILE" | sed 's/.*python:v\(.*\)-noble.*/\1/')

if [[ -z "$PLAYWRIGHT_VERSION" ]]; then
  echo "Could not find a pinned 'playwright==<version>' in $REQUIREMENTS_FILE." >&2
  exit 1
fi

if [[ -z "$IMAGE_TAG" ]]; then
  echo "Could not find a 'container: mcr.microsoft.com/playwright/python:v<version>-noble' in $WORKFLOW_FILE." >&2
  exit 1
fi

if [[ "$PLAYWRIGHT_VERSION" != "$IMAGE_TAG" ]]; then
  echo "Playwright version mismatch:" >&2
  echo "  $REQUIREMENTS_FILE pins playwright==$PLAYWRIGHT_VERSION" >&2
  echo "  $WORKFLOW_FILE uses container tag v$IMAGE_TAG-noble" >&2
  echo "Bump the e2e container tag in $WORKFLOW_FILE to v$PLAYWRIGHT_VERSION-noble (or pin requirements/dev.txt to $IMAGE_TAG)." >&2
  exit 1
fi

echo "OK: playwright==$PLAYWRIGHT_VERSION matches e2e container tag v$IMAGE_TAG-noble."