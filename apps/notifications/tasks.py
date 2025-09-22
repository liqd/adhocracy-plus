from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from adhocracy4.phases.models import Phase
from apps.offlineevents.models import OfflineEvent

from .models import NotificationType
from .signals.helpers import _create_notifications
from .strategies import OfflineEventReminder
from .strategies import PhaseEnded
from .strategies import PhaseStarted
from .strategies import ProjectStarted
from .strategies import ProjectEnded


# TODO: Run daily (?) via celery
@shared_task
def send_recently_started_project_notifications():
    """
    Send notifications to project followers for project completed
    """
    now = timezone.now()
    last_check = now - timedelta(hours=24)

    started_phases = Phase.objects.filter(
        Q(start_date__gte=last_check, start_date__lte=now)
    )

    started_projects = [p.module.project for p in started_phases if p.starts_first_of_project]

    strategy = ProjectStarted()
    for project in started_projects:
        _create_notifications(project, strategy)

    return


# TODO: Add this as prop in a4
def is_last_phase_in_project(phase):
    project = phase.module.project
    phases = project.phases.filter(module__is_draft=False).order_by(
        ("-end_date")
    )
    is_last_phase = phase == phases[0]
    return is_last_phase


@shared_task
def send_recently_completed_project_notifications():
    """
    Send notifications to project followers for project completed
    """
    now = timezone.now()
    last_check = now - timedelta(hours=24)

    completed_phases = Phase.objects.filter(
        Q(end_date__gte=last_check, end_date__lte=now)
    )

    ended_projects = [p.module.project for p in completed_phases if is_last_phase_in_project(p)]
    strategy = ProjectEnded()
    for project in ended_projects:
        _create_notifications(project, strategy)

    return


# TODO: Run daily (?) via celery
@shared_task
def send_upcoming_event_notification():
    """
    Send notifications to project followers for events starting within 24 hours
    """

    now = timezone.now()
    tomorrow = now + timedelta(hours=24)

    upcoming_events = OfflineEvent.objects.filter(
        Q(date__gte=now, date__lte=tomorrow)
    ).select_related("project")

    strategy = OfflineEventReminder()

    for event in upcoming_events:
        if not event.project:
            continue

        _create_notifications(event, strategy)

    return
