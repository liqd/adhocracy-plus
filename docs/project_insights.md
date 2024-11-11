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

## Developer Notes

Initially we thought about simply writing a query that counts all relevant objects (comments, ratings, ideas, ...), but we anticipated that it would be too slow for the project view to be queried on every page load.

We then decided to create a "data model", a table whose only purpose is to hold all insights numbers of a project. The result is the model "ProjectInsights".

The next problem was how do we initialise this table and how do we keep it up to date when data changes? One approach we discussed was a background task that updates the table every hour, for example, by running a query that counts all objects. It was decided that this is not up to date enough ("if I create a comment now, it should increase the comment count in the insights page immediately"). Hence we decided to create signals that update our insights table every time that ideas, comments, ratings etc are created or removed. This lead to a few tricky questions:

- should we decrease the count if a comment (for example) is deleted?
- should we decrease the active participants count if all contributions are removed from a project?

Also we discovered that whereas the number of comments and ideas can be a simple integer (simple increase or decrease when a comment is created or deleted), the number of active participants must be stored by a many-to-many relation because an active participant can author many objects and we only want to increase the number of active participants if it is the first contribution by that user.

We solved all challenges of keeping the data up to date by creating signals for the respective objects (ideas, comments, ratings etc).

Finally, we decided that we want to add a custom migration that initializes the insights table for all existing projects. The idea here was that our software is open source and people updating our software should be able to see the insights data without running management or deployment commands. The custom migration, on the other hand, is applied while installing or updating the software.

The custom migration (0006_initialize_insights.py) was hard to write because of the limited query manager access in custom migrations (Django's fake migration models). In particular, the generic relations on ratings and comments forced us to migrate by "looping and counting".

Finally, we added a management command ("reset_insights_table") to refresh the insights table. This code makes use of regular models (instead of Django's fake migration models) and can therefore be tested and keeps our options open for future background tasks and bug fixes.

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
`unregistered_participants` field which stores this number.
