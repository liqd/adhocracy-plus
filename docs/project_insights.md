## Structure

### frontend

- adhocracy-plus/assets/scss/components/\_data_table.scss
- adhocracy-plus/templates/a4dashboard/includes/project_result_form.html
- apps/projects/templates/a4_candy_projects/project_detail.html

### backend

- apps/projects/dashboard.py
- apps/projects/insights.py
- apps/projects/management/commands/reset_insights_table.py
- apps/projects/models.py
- apps/projects/signals.py
- apps/projects/views.py

### a4

- adhocracy4/projects/mixins.py

### migrations

- apps/projects/migrations/0005_projectinsight.py
- apps/projects/migrations/0006_initialize_insights.py

## Background

The feature "Project Insights" is displaying a summary of user activity in the project details page. Among other numbers it should display how many active participants there are, how many ideas and comments were created and how many poll answers were submitted.

## How it works

### Purpose

Instead of counting contributions on every page load, the app keeps a **pre-aggregated cache** per project in the `ProjectInsight` model. Counts are updated incrementally via Django signals so the UI stays current without expensive queries on each request.

A full recount (`create_insight()`) remains available for repair and ops; see `reset_insights_table` below.

### Data model

`ProjectInsight` in `apps/projects/models.py` — one row per project (`OneToOneField` to `Project`).

| Field | What it counts |
|---|---|
| `comments` | Visible project comments (see inclusion rules below) |
| `ratings` | Thumbs up/down on ideas, map ideas, topics, comments, and proposals; plus likes on live questions |
| `written_ideas` | Ideas, map ideas, proposals, and topics |
| `poll_answers` | Poll votes and open answers |
| `live_questions` | Interactive-event questions |
| `active_participants` | Registered users who contributed (M2M — each user counted once) |
| `unregistered_participants` | Anonymous poll voters (integer — distinct `content_id` values) |
| `display` | Whether stats are shown on the public project page |

The displayed participant total is `active_participants.count() + unregistered_participants`.

### Inclusion rules (`apps/projects/insights.py`)

Helpers in `insights.py` define **which content counts**. They are shared by `create_insight()` (full recount) and `apps/projects/signals.py` (incremental updates) so both paths stay aligned.

Not every database row counts:

- **Draft modules** — content on `is_draft=True` modules is excluded until published. Toggling a module's draft state triggers a full `create_insight()` for that project.
- **Comments** — soft-deleted (`is_removed`), moderator-deleted (`is_censored`), and blocked (`is_blocked`) comments are excluded. Comment "delete" in the API does not remove the row (no `post_delete`); signals use `comment_counts_toward_insights()` on each save to detect when a comment enters or leaves the counted set. Hard deletes (e.g. cascade when a parent idea is removed) use a `pre_delete` cache so `post_delete` still knows whether the comment counted.
- **Ratings** — only thumbs up/down (`value` ±1) count. "Removing" a rating sets `value` to 0 without deleting the row; signals adjust the counter on value change.
- **Budgeting proposals** — archived proposals (`is_archived=True`) are excluded from `written_ideas`; toggling archive state updates the counter (same `pre_save` / `post_save` pattern as comments).
- **Live questions** — hidden questions (`is_hidden=True`) are excluded from `live_questions`; toggling visibility updates the counter.
- **Unregistered voters** — counted by distinct `content_id`, not per Vote/Answer row.

Key helpers:

| Function | Purpose |
|---|---|
| `comment_counts_toward_insights()` | Should this comment count toward `insight.comments`? |
| `written_idea_counts_toward_insights()` | Should this idea/map idea/topic/proposal count toward `written_ideas`? |
| `live_question_counts_toward_insights()` | Should this live question count toward `live_questions`? |
| `module_counts_toward_insights()` | Is this module published enough to count? |
| `rating_counts_toward_insights()` | Does this rating value (±1 vs 0) count? |
| `get_counted_comments_project()` | Comments included in a full recount |
| `count_unregistered_participants()` | Distinct anonymous voters for recount / sync |
| `user_has_active_contributions()` | Does a user still have any counted contributions? (used on delete) |

### Keeping counts up to date (signals)

Signals are registered in `apps/projects/apps.py` → `apps/projects/signals.py`.

**On create** — `post_save` handlers increment the matching counter and add the creator to `active_participants` where applicable.

**On hard delete** — `post_delete` handlers decrement counters. Where a handler also added a participant, it calls `remove_active_participant_if_inactive()` so users are only removed when they have no remaining contributions.

**Cascade deletes** — when Django removes related rows in one operation (e.g. deleting an idea removes its ratings and comments), foreign keys and generic relations may already be cleared in `post_delete`. Handlers that walk relations (`Rating.module`, `Vote.choice`, `Like.livequestion`, etc.) register `pre_delete` to cache the module or counted state on the instance (`_insight_delete_module`, `_insight_delete_was_counted`) and read that cache in `post_delete`.

**On soft state change** — comments, ratings, archived proposals, and hidden live questions use `pre_save` / `post_save` to detect transitions into or out of the counted set (same pattern as hard delete/increment).

**Poll participation** — split across two mechanisms:

- `Vote` / `Answer` `post_save` → `poll_answers`
- `poll_voted` signal → `active_participants` (registered) or `sync_unregistered_participants()` (anonymous)

Models wired up: `Comment`, `Idea`, `MapIdea`, `Proposal`, `Topic`, `Rating`, `LiveQuestion`, `Like`, `Vote`, `Answer`, `Module` (draft changes), and `poll_voted`.

### Full recalculation

When counters may have drifted (bulk admin actions, legacy data, after deploy):

- **`create_insight(project)`** — queries all relevant objects and overwrites every field on `ProjectInsight`
- **`create_insights(projects)`** — batch wrapper
- **Management command:** `python manage.py reset_insights_table [--project SLUG]`

The command snapshots counts before and after each project and **prints a line only when something changed**, e.g.:

```
my-slug (id=42, name='My Project'): comments 5 -> 3, active_participants 3 -> 2
```

A nightly cron calling this command is a reasonable safety net; signals handle real-time updates for normal use.

### Display

**`create_insight_context(insight)`** in `apps/projects/models.py` builds template context (`counts`, `insight_label`). Which rows appear depends on **active (non-draft) module blueprint types** — e.g. poll answers only if the project has a poll module (`"PO"`). Topic prioritization (`"TP"`) is included in the written-ideas row.

**`ProjectInsight.update_context(project, context, dashboard=False)`** adds that context when `insight.display` is true, or always in the dashboard.

**Views:** `ProjectDetailView`, `ProjectResultsView`, and `ProjectResultInsightComponentFormView` (dashboard toggle via `ProjectInsightForm` in `apps/projects/dashboard.py`).

Templates: `project_detail_insights.html`, `project_insight_stats.html`.

### Known gaps

- Bulk operations or raw SQL that bypass Django signals can drift until `reset_insights_table` runs.

### Tests

`tests/projects/test_insights.py` covers incremental updates (create/delete, soft comment delete, rating value changes, draft modules, cascade deletes with ratings and comments, vote/like deletes, archived proposals, hidden live questions, and unregistered poll voters). Run:

```bash
venv/bin/python -m pytest tests/projects/test_insights.py -v
```

## Developer Notes

Initially we thought about simply writing a query that counts all relevant objects (comments, ratings, ideas, ...), but we anticipated that it would be too slow for the project view to be queried on every page load.

We then decided to create a "data model", a table whose only purpose is to hold all insights numbers of a project. The result is the model "ProjectInsights".

The next problem was how do we initialise this table and how do we keep it up to date when data changes? One approach we discussed was a background task that updates the table every hour, for example, by running a query that counts all objects. It was decided that this is not up to date enough ("if I create a comment now, it should increase the comment count in the insights page immediately"). Hence we decided to create signals that update our insights table every time that ideas, comments, ratings etc are created or removed. This lead to a few tricky questions:

- should we decrease the count if a comment (for example) is deleted?
- should we decrease the active participants count if all contributions are removed from a project?

Also we discovered that whereas the number of comments and ideas can be a simple integer (simple increase or decrease when a comment is created or deleted), the number of active participants must be stored by a many-to-many relation because an active participant can author many objects and we only want to increase the number of active participants if it is the first contribution by that user.

Decrement-on-delete, participant cleanup, soft-deleted comments, rating value changes, draft-module exclusion, and related behaviour are documented in **How it works** above and implemented in `apps/projects/signals.py` and `apps/projects/insights.py`.

Finally, we decided that we want to add a custom migration that initializes the insights table for all existing projects. The idea here was that our software is open source and people updating our software should be able to see the insights data without running management or deployment commands. The custom migration, on the other hand, is applied while installing or updating the software.

The custom migration (0006_initialize_insights.py) was hard to write because of the limited query manager access in custom migrations (Django's fake migration models). In particular, the generic relations on ratings and comments forced us to migrate by "looping and counting".

Finally, we added a management command (`reset_insights_table`) to refresh the insights table. This code makes use of regular models (instead of Django's fake migration models) and can therefore be tested and keeps our options open for future background tasks and bug fixes. The command reports per-project corrections when counts change (see **How it works**).

## Updates

- With the new feature of the poll module optionally allowing unregistered users
  to vote, we had to find a way for the number of participants to include
unregistered users, as currently they are tied to the user as part of a m2m
relation. We introduced a new base model `GeneratedContent` which has an
optional field `creator` which is used if a registered user participated and an optional field
`content_id` for unregistered users. In case of a poll submission from an
unregistered user a unique uuid4 is created and
stored in `content_id` to allow counting the amount of unregistered users which
participated in the poll. We extended the `ProjectInsight` model with a
`unregistered_participants` field which stores this number. Anonymous voters are
synced by distinct `content_id` (see `count_unregistered_participants()`).

- Incremental signals were extended with `post_delete` handlers, soft-delete
  handling for comments, rating value changes, draft-module exclusion, proposal
  ratings in recounts, archived/hidden exclusion for proposals and live questions,
  `pre_delete` caching for cascade-safe decrements, and shared inclusion helpers
  in `insights.py` so signals and `create_insight()` use the same rules.
