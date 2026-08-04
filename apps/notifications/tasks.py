from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from adhocracy4.phases.models import Phase
from apps.offlineevents.models import OfflineEvent

from .models import Notification
from .models import NotificationType
from .services import NotificationService
from .strategies import OfflineEventReminder
from .strategies import ProjectEnded
from .strategies import ProjectStarted


def _hours(setting_name, default):
    """Read a notification window setting in hours (default 72)."""
    return getattr(settings, setting_name, default)


def _project_already_notified(project, notification_type) -> bool:
    """True if a notification of this type already exists for the project.

    Mirrors the idempotency of adhocracy4's ``create_system_actions``
    management command: the first run within the coverage window creates the
    notification (and sends the email), later runs skip it so every project
    is only notified once.
    """
    return Notification.objects.filter(
        project=project, notification_type=notification_type
    ).exists()


def _event_already_notified(event) -> bool:
    """True if an upcoming-event notification already exists for the event."""
    return Notification.objects.filter(
        notification_type=NotificationType.EVENT_SOON,
        target_url=event.get_absolute_url(),
    ).exists()


@shared_task(name="send_recently_started_project_notifications")
def send_recently_started_project_notifications():
    """
    Notify followers that a project's first phase has started.

    Effective timing: the task runs daily and looks back
    NOTIFICATION_PROJECT_STARTED_HOURS (default 72h), so a project is notified
    at the first run after its start date - i.e. within ~24h of the start. The
    lookback is a safety margin so backdated starts or missed runs are still
    caught. Deduplication guarantees each project is notified exactly once.
    """
    now = timezone.now()
    window = timedelta(hours=_hours("NOTIFICATION_PROJECT_STARTED_HOURS", 72))
    last_check = now - window

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
        if _project_already_notified(project, NotificationType.PROJECT_STARTED):
            continue
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
    Notify followers that a project has been completed.

    Effective timing: the task runs daily and looks back
    NOTIFICATION_PROJECT_COMPLETED_HOURS (default 72h), so a project is
    notified at the first run after its last phase ends - i.e. within ~24h of
    the end. The lookback is a safety margin so missed runs are still caught.
    Deduplication guarantees each project is notified exactly once.
    """
    now = timezone.now()
    window = timedelta(hours=_hours("NOTIFICATION_PROJECT_COMPLETED_HOURS", 72))
    last_check = now - window

    completed_phases = Phase.objects.filter(
        Q(end_date__gte=last_check, end_date__lte=now)
    )

    ended_projects = [
        p.module.project for p in completed_phases if is_last_phase_in_project(p)
    ]
    strategy = ProjectEnded()
    for project in ended_projects:
        if _project_already_notified(project, NotificationType.PROJECT_COMPLETED):
            continue
        NotificationService.create_notifications(project, strategy)

    return


@shared_task(name="send_upcoming_event_notifications")
def send_upcoming_event_notifications():
    """
    Remind followers of events starting soon.

    Effective timing: the task runs daily and looks ahead
    NOTIFICATION_EVENT_STARTING_HOURS (default 72h), so an event is notified at
    the first run after it enters the window - i.e. roughly 48-72h before the
    event (sooner for events announced after they entered the window).
    Deduplication guarantees each event is notified exactly once.
    """

    now = timezone.now()
    future = now + timedelta(hours=_hours("NOTIFICATION_EVENT_STARTING_HOURS", 72))

    upcoming_events = OfflineEvent.objects.filter(
        Q(date__gte=now, date__lte=future)
    ).select_related("project")

    strategy = OfflineEventReminder()

    for event in upcoming_events:
        if not event.project:
            continue

        if _event_already_notified(event):
            continue

        NotificationService.create_notifications(event, strategy)

    return
