#!/bin/bash

# Path to pyproject file
PYPROJECT_FILE="pyproject.toml"

# Path to package.json file
PACKAGE_JSON_FILE="package.json"

# Package name
PACKAGE_NAME="adhocracy4"

# Read the git rev from [tool.uv.sources]
PIP_HASH=$(sed -n 's/^adhocracy4 = { git = .*rev = "\([^"]*\)" }$/\1/p' "$PYPROJECT_FILE")

# Read the commit hash from the package.json file
PACKAGE_JSON_HASH=$(jq -r ".dependencies.\"$PACKAGE_NAME\"" "$PACKAGE_JSON_FILE" | awk -F'#' '{print $2}')

# Check if the hashes match
if [[ "$PIP_HASH" != "$PACKAGE_JSON_HASH" ]]; then
  echo "Hash for $PACKAGE_NAME does not match between pyproject.toml and package.json."
  echo "pyproject.toml rev: $PIP_HASH"
  echo "package.json hash: $PACKAGE_JSON_HASH"
  exit 1
fi
