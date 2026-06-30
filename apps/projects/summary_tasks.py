"""Celery tasks for periodic project summary generation."""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from sentry_sdk import capture_exception

from adhocracy4.projects.models import Project
from apps.contrib.models import Settings
from apps.summarization.models import ProjectSummary

from .utils import generate_project_summary
from .utils import is_ai_summarisation_enabled

logger = logging.getLogger(__name__)


@shared_task(name="generate_project_summary_task")
def generate_project_summary_task(project_id):
    """
    Generate AI summary for a single project. Used by the periodic refresh task.
    On exception only logs (and Sentry); the next Beat run will retry.
    """
    try:
        project = (
            Project.objects.select_related("organisation").filter(pk=project_id).first()
        )
        if not project:
            logger.warning(
                "generate_project_summary_task: project %s not found", project_id
            )
            return
        if not is_ai_summarisation_enabled(project):
            logger.debug(
                "generate_project_summary_task: skipping project %s "
                "(AI summarisation disabled)",
                project_id,
            )
            return
        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", None)
        generate_project_summary(
            project,
            request=None,
            base_url=base_url,
            allow_regeneration=True,
        )
        logger.info(
            "generate_project_summary_task: summary generated for project %s (%s)",
            project_id,
            project.slug,
        )
    except Exception as exc:
        logger.error(
            "generate_project_summary_task failed for project %s: %s",
            project_id,
            exc,
            exc_info=True,
        )
        capture_exception(exc)


@shared_task(name="refresh_project_summaries")
def refresh_project_summaries():
    """
    Find AI-enabled projects with no summary younger than max_age and enqueue
    one task per project.
    """
    max_age_minutes = Settings.get_int("project_summary_auto_refresh_max_age_minutes")
    max_per_run = getattr(
        settings, "PROJECT_SUMMARY_AUTO_REFRESH_MAX_PROJECTS_PER_RUN", 0
    )
    cutoff = timezone.now() - timedelta(minutes=max_age_minutes)

    projects = Project.objects.filter(
        organisation__enable_ai_summarisation=True,
        is_draft=False,
    ).order_by("pk")

    enqueued = 0
    for project in projects:
        if max_per_run > 0 and enqueued >= max_per_run:
            break
        latest = (
            ProjectSummary.objects.filter(project=project)
            .order_by("-created_at")
            .first()
        )
        if latest is None or latest.created_at < cutoff:
            generate_project_summary_task.delay(project.id)
            enqueued += 1

    if enqueued:
        logger.info(
            "refresh_project_summaries: enqueued %s project summary tasks", enqueued
        )
