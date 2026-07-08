# Custom management commands

From the project root directory run: `python manage.py <command> [args]`

## Commands

**cleanup_unverified_users** `<days>` `<test>`

- Removes users who registered more than n days ago but never logged in (e.g. never verified email).
- `test` must be `True` or `False` (run without deletion when `True`).

**create_offlineevent_system_actions**

- Creates system actions for offline events that start within the configured hours.
- Used to notify followers about upcoming events.

**export_project_data** `[project_name]`

- Exports project data by project name (partial match allowed).
- Prompts for name if omitted; supports selecting multiple or all matching projects.

**import_geodata** `[--gdal-legacy]`

- Imports Berlin GEO data (Bezirke, Bezirksregionen) as map presets.
- Use `--gdal-legacy` for GDAL ≤ 1.10.

**makemessages**

- Extended Django makemessages: includes a4 and adhocracy-plus paths, disables fuzzy matching.
- Use same args as Django's `makemessages` (e.g. `-l de`, `-d djangojs`).

**reset_insights_table** `[--project SLUG]`

- Rebuilds project insight counters from the database (`create_insight()`).
- Optional `--project` to reset a single project only.
- Prints a line per project only when counts change (see `docs/project_insights.md`).

**send_publish_results_reminder** `<project-slug>` `[--force]`

- Sends the publish-results reminder to every initiator of the project's organisation (one e-mail per initiator).
- Uses the same eligibility rules as automatic sending (phase end, delay, empty results, etc.).
- `--force` bypasses all checks and does not update `results_reminder_sent_at` (manual testing only).
- Django admin → Projects → actions uses the same rules (without `--force`).

**send_test_emails** `<email>`

- Sends a set of test emails (account, notifications, etc.) to a registered user.
- Useful for checking email templates and delivery.

**send_test_newsletter** `<email>` `[--subject]` `[--body]` `[--organisation-pk]` `[--ignore-preferences]` `[--debug]`

- Sends a test newsletter synchronously to one recipient.
- `--debug` prints diagnostics; `--ignore-preferences` bypasses opt-out.

