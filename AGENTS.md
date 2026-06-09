# Agent instructions

Applies to all code and config in this repository unless a file or directory explicitly documents a different convention.

## Code language

- **Comments** must be written in **English** (including SCSS, templates, and shell scripts).
- **Variable names** (and other identifiers: functions, classes, modules where naming is chosen in this project) must be in **English**.

## Python interpreter

- Use the project virtual environment’s Python: **`venv/bin/python`** (relative to the repository root).
- Do not assume a system-wide `python` or `python3` unless explicitly required; prefer `venv/bin/python` for installs, scripts, and tooling that should match project dependencies.

## Frontend assets

- **`npm run build`** is usually **not** needed during development: **`make watch`** already runs **`npm run watch`** (alongside the Django dev server), which rebuilds JS and CSS when sources change. Run **`npm run build`** only when you need a one-off full build without the watch process (e.g. CI-style checks or troubleshooting).

### Static images and SVGs

- **Never create or edit files under `adhocracy-plus/static/`** — that directory is **gitignored build output** (`npm run build` / `make watch`). Deploy and `collectstatic` will not see files that exist only there.
- **Source path for shared images** referenced as `{% static 'images/...' %}`: put files in **`adhocracy-plus/assets/images/`** (webpack `CopyWebpackPlugin` copies them to `static/images/` on build).
- **App-specific static files**: use **`apps/<app>/static/`** (collected directly by Django).
- After adding an image, confirm it appears under **`assets/`** (or `apps/.../static/`) in git — not only under `static/`.

## Changelog

- For **release notes and user-facing change history**, edit **`CHANGELOG.md`** at the repository root **only**. Do not add duplicate changelog content to `README.md`, wiki files, or other docs unless a maintainer explicitly asks for it.
