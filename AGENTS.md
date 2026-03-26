# Agent instructions

Applies to all code and config in this repository unless a file or directory explicitly documents a different convention.

## Code language

- **Comments** must be written in **English** (including SCSS, templates, and shell scripts).
- **Variable names** (and other identifiers: functions, classes, modules where naming is chosen in this project) must be in **English**.

## Python interpreter

- Use the project virtual environment’s Python: **`venv/bin/python`** (relative to the repository root).
- Do not assume a system-wide `python` or `python3` unless explicitly required; prefer `venv/bin/python` for installs, scripts, and tooling that should match project dependencies.
