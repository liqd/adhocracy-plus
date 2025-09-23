from datetime import timedelta

import pytest
from django.utils import timezone

from adhocracy4.follows.models import Follow
from apps.notifications.models import Notification
from apps.notifications.tasks import send_recently_completed_project_notifications
from apps.notifications.tasks import send_recently_started_project_notifications
from apps.notifications.tasks import send_upcoming_event_notifications


@pytest.mark.django_db
def test_send_recently_started_project_notifications(
    phase_factory, project_factory, user2
):
    """Check if notifications are sent for recently started projects."""
    project = project_factory()

    # Create only one phase for this project so it's the first
    phase = phase_factory(
        module__project=project,
        start_date=timezone.now() - timedelta(hours=12),
        end_date=timezone.now() + timedelta(days=7),
    )

    # Make user 2 a follower of the project
    Follow.objects.get_or_create(
        project=project,
        creator=user2,
        defaults={
            "enabled": True,
        },
    )

    send_recently_started_project_notifications()

    created_notifications = Notification.objects.filter(recipient=user2)
    assert created_notifications.count() == 1


@pytest.mark.django_db
def test_send_recently_completed_project_notifications(
    phase_factory, project_factory, user2
):
    """Check if notifications are sent for recently compleed projects."""
    project = project_factory()

    # Create only one phase for this project so it's the first
    phase = phase_factory(
        module__project=project,
        start_date=timezone.now() - timedelta(days=7),
        end_date=timezone.now() - timedelta(hours=12),
    )

    # Make user 2 a follower of the project
    Follow.objects.get_or_create(
        project=project,
        creator=user2,
        defaults={
            "enabled": True,
        },
    )

    send_recently_completed_project_notifications()

    created_notifications = Notification.objects.filter(recipient=user2)
    assert created_notifications.count() == 1


@pytest.mark.django_db
def test_send_upcoming_event_notifications(
    project_factory, offline_event_factory, user2
):
    project = project_factory()
    offline_event = offline_event_factory(
        project=project,
        date=timezone.now() + timedelta(hours=12),
    )

    # Make user 2 a follower of the project
    Follow.objects.get_or_create(
        project=project,
        creator=user2,
        defaults={
            "enabled": True,
        },
    )

    send_upcoming_event_notifications()

    created_notifications = Notification.objects.filter(recipient=user2)
    assert created_notifications.count() == 1
