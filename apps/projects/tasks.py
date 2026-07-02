import importlib

from celery import shared_task
from django.utils import timezone

from adhocracy4.projects.models import Project

from .publish_results_reminder import get_publish_results_reminder_skip_reason
from .publish_results_reminder import send_publish_results_reminder
from .summary_tasks import generate_project_summary_task  # noqa: F401
from .summary_tasks import refresh_project_summaries  # noqa: F401


@shared_task
def send_async_no_object(email_module_name, email_class_name, object, args, kwargs):
    email_module = importlib.import_module(email_module_name)
    email_class = getattr(email_module, email_class_name)
    email_class().dispatch(object, *args, **kwargs)


@shared_task(name="send_publish_results_reminders")
def send_publish_results_reminders() -> None:
    """Remind initiators to publish results after online participation ends (delay
    and optional RESULTS_PUBLISH_REMINDER_MIN_LAST_PARTICIPATION_END)."""
    now = timezone.now()

    projects = (
        Project.objects.filter(
            project_type="a4projects.Project",
            is_draft=False,
            is_archived=False,
        )
        .select_related("organisation", "insight")
        .prefetch_related(
            "module_set",
            "module_set__phase_set",
            "organisation__initiators__notification_settings",
        )
    )

    for project in projects:
        if get_publish_results_reminder_skip_reason(project, now=now) is not None:
            continue
        send_publish_results_reminder(project, now=now)
