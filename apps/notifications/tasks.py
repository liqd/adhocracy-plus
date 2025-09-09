from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from adhocracy4.phases.models import Phase
from apps.offlineevents.models import OfflineEvent

from .models import NotificationType
from .signals.helpers import _create_notifications
from .strategies import OfflineEventReminderStrategy
from .strategies import PhaseEndedStrategy
from .strategies import PhaseStartedStrategy


# TODO: Run daily (?) via celery
@shared_task
def send_recently_started_phase_notifications():
    """
    Send notifications to project followers for project completed
    """
    now = timezone.now()
    last_check = now - timedelta(hours=24)

    started_phases = Phase.objects.filter(
        Q(start_date__gte=last_check, start_date__lte=now)
    )

    strategy = PhaseStartedStrategy()
    for phase in started_phases:
        _create_notifications(phase, strategy)

    return


@shared_task
def send_recently_completed_phase_notifications():
    """
    Send notifications to project followers for project completed
    """
    now = timezone.now()
    last_check = now - timedelta(hours=24)

    completed_phases = Phase.objects.filter(
        Q(end_date__gte=last_check, end_date__lte=now)
    )

    strategy = PhaseEndedStrategy()
    for phase in completed_phases:
        _create_notifications(phase, strategy)

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

    strategy = OfflineEventReminderStrategy()

    for event in upcoming_events:
        if not event.project:
            continue

        _create_notifications(event, strategy)

    return
