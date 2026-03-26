---
name: frontend-workflow
description: After frontend changes, verifies the UI in the browser and compares it to Figma or a reference image. Use when working on SCSS/CSS, templates (HTML/Django), JavaScript, UI components, accessibility, or visual layout; or when the user mentions Figma, screenshots, or design review.
---

# Frontend workflow (adhocracy+)

## Goal

After relevant frontend changes, do **not** rely on code alone—**see the result in the browser** and, when possible, compare it to the **design (Figma)** or a **reference image**.

## When to apply

- Styles under `adhocracy-plus/assets/`, templates under `apps/**/templates/`, frontend JS, or translations with visible UI impact were added or changed.
- The user mentions a **Figma URL**, a **mockup**, or **“match the design”**.

## Steps

### 1. Dev server

- **`make watch`** starts the dev server on **port `8004`** (not `8000`). Prefer **`http://127.0.0.1:8004/`** as the base URL unless the user or terminal shows something else.
- The server is **often already running**—check before starting another instance; only run `make server` / `make watch` if nothing is listening or the user asks to start it.
- **Local URL and login** (including password): see **[README.md](../../../README.md)** (section *Start a local server*).

### 2. Verify in the browser

- Use **Browser MCP**: navigate to the affected page (or derive the route from the task/ticket).
- Take a **snapshot**; check relevant states (e.g. hover, open menu); if needed, wait briefly and check again.
- Watch for **regressions** (layout, spacing, typography, contrast, focusable elements).

**Spacing / distances (when precision matters):**

- Use **`browser_get_bounding_box`** with the element **`ref`** from **`browser_snapshot`** to read geometry and **derive spacing** (gaps, margins, alignment) from the **relationship between bounding boxes**—do not rely on screenshots alone for numeric layout checks.
- If that is **unreliable or insufficient** (e.g. iframes, shadow DOM, unclear refs, or you need **computed CSS** values), use **Playwright** (small script or test in the repo) to measure spacing in the **actual rendered layout**: e.g. `locator.boundingBox()`, `getComputedStyle`, or `getBoundingClientRect()` via `page.evaluate`.

### 3. Design comparison

**Figma available (URL from user or ticket):**

- **Figma MCP**: use `get_design_context` (or the server’s equivalent) with `fileKey` and `nodeId` from the URL; for `node-id` in the URL, replace hyphens with colons.
- Compare typography, spacing, colors, breakpoints—be pragmatic, not obsessively pixel-perfect, but fix or call out obvious deviations.

**No Figma:**

- Use a **screenshot, export, or reference image** from the issue/chat if provided.
- Otherwise **describe** what you see in the browser and ask the user for a Figma URL or image if comparison is needed.

### 4. Finish the reply

Briefly note:

- [ ] Checked in the browser (URL).
- [ ] Design: Figma / reference image / no reference.
- [ ] If spacing/layout precision was required: **bounding box** (Browser MCP) and/or **Playwright**—state which was used.

## Notes

- **Iframes**: automation often only sees the top frame—mention embedded content to the user if relevant.
- **Local assets**: after SCSS changes, ensure a build is running (`make watch`) or assets are built as usual before judging the result.

## Additional files

- Optionally add project-specific URLs or screenshots in [reference.md](reference.md) (one level deep from `SKILL.md`).
