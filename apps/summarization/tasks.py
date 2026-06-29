"""Celery tasks for periodic AI project summary refresh."""

import logging

from celery import shared_task
from sentry_sdk import capture_exception

from adhocracy4.projects.models import Project

from .project_summary import generate_project_summary
from .project_summary import get_auto_refresh_max_projects_per_run
from .project_summary import is_ai_summarisation_enabled
from .project_summary import project_needs_summary_refresh

logger = logging.getLogger(__name__)


def get_projects_due_for_summary_refresh():
    """
    Return non-draft projects in AI-enabled organisations due for Beat refresh.

    Roots-style: no summary or summary older than max_age only.
    """
    max_per_run = get_auto_refresh_max_projects_per_run()
    due = []

    projects = Project.objects.filter(
        organisation__enable_ai_summarisation=True,
        is_draft=False,
    ).order_by("pk")

    for project in projects:
        if project_needs_summary_refresh(project):
            due.append(project)
        if max_per_run > 0 and len(due) >= max_per_run:
            break

    return due


@shared_task(name="refresh_project_summary")
def refresh_project_summary(project_id: int) -> None:
    """Generate or refresh the AI summary for a single project."""
    try:
        project = Project.objects.select_related("organisation").get(pk=project_id)
    except Project.DoesNotExist:
        logger.warning("Project %s not found for summary refresh", project_id)
        return

    if not is_ai_summarisation_enabled(project):
        logger.debug(
            "Skipping summary refresh for project %s (AI summarisation disabled)",
            project_id,
        )
        return

    try:
        generate_project_summary(project, allow_regeneration=True)
        logger.info(
            "Summary refresh completed for project %s (%s)", project.pk, project.slug
        )
    except Exception as exc:
        logger.exception("Failed to refresh summary for project %s", project_id)
        capture_exception(exc)


@shared_task(name="refresh_project_summaries")
def refresh_project_summaries() -> None:
    """
    Enqueue summary tasks for eligible projects (Roots-style scheduling).

    A project is enqueued when it has no summary or its latest summary is older
    than project_summary_auto_refresh_max_age_minutes. Hash-based change detection
    runs inside generate_project_summary when each task executes.
    """
    due_projects = get_projects_due_for_summary_refresh()
    if not due_projects:
        logger.debug("No projects due for summary refresh")
        return

    for project in due_projects:
        refresh_project_summary.delay(project.pk)

    logger.info("Enqueued summary refresh for %s project(s)", len(due_projects))
