from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from adhocracy4.phases.models import Phase
from apps.offlineevents.models import OfflineEvent

from .services import NotificationService
from .strategies import OfflineEventReminder
from .strategies import ProjectEnded
from .strategies import ProjectStarted


@shared_task(name="send_recently_started_project_notifications")
def send_recently_started_project_notifications():
    """
    Send notifications to project followers for project started
    """
    now = timezone.now()
    last_check = now - timedelta(hours=24)

    started_phases = Phase.objects.filter(
        Q(start_date__gte=last_check, start_date__lte=now)
    )

    # Ensure no duplicates
    seen_projects = set()
    started_projects = []

    for phase in started_phases:
        if phase.starts_first_of_project and phase.module.project:
            project = phase.module.project
            if project.id not in seen_projects:
                seen_projects.add(project.id)
                started_projects.append(project)

    strategy = ProjectStarted()
    for project in started_projects:
        NotificationService.create_notifications(project, strategy)

    return len(started_projects)


# TODO: Add this as prop in a4
def is_last_phase_in_project(phase):
    project = phase.module.project
    phases = project.phases.filter(module__is_draft=False).order_by(("-end_date"))
    is_last_phase = phase == phases[0]
    return is_last_phase


@shared_task(name="send_recently_completed_project_notifications")
def send_recently_completed_project_notifications():
    """
    Send notifications to project followers for project completed
    """
    now = timezone.now()
    last_check = now - timedelta(hours=24)

    completed_phases = Phase.objects.filter(
        Q(end_date__gte=last_check, end_date__lte=now)
    )

    ended_projects = [
        p.module.project for p in completed_phases if is_last_phase_in_project(p)
    ]
    strategy = ProjectEnded()
    for project in ended_projects:
        NotificationService.create_notifications(project, strategy)

    return


@shared_task(name="send_upcoming_event_notifications")
def send_upcoming_event_notifications():
    """
    Send notifications to project followers for events starting within 24 hours
    """

    now = timezone.now()
    future = now + timedelta(hours=72)

    upcoming_events = OfflineEvent.objects.filter(
        Q(date__gte=now, date__lte=future)
    ).select_related("project")

    strategy = OfflineEventReminder()

    for event in upcoming_events:
        if not event.project:
            continue

        NotificationService.create_notifications(event, strategy)

    return
