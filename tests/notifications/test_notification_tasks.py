from datetime import timedelta

import pytest
from django.utils import timezone

from adhocracy4.follows.models import Follow
from apps.notifications.models import Notification
from apps.notifications.models import NotificationType
from apps.notifications.tasks import send_recently_completed_project_notifications
from apps.notifications.tasks import send_recently_started_project_notifications
from apps.notifications.tasks import send_upcoming_event_notifications
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_send_recently_started_project_notifications(
    phase_factory, project_factory, user2
):
    """Check if notifications are sent for recently started projects."""
    project = project_factory()

    # Create only one phase for this project so it's the first
    phase_factory(
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
    assert (
        created_notifications.first().notification_type
        == NotificationType.PROJECT_STARTED
    )

    follower_emails = get_emails_for_address(user2.email)
    assert len(follower_emails) == 1
    assert project.name.lower() in follower_emails[0].subject.lower()


@pytest.mark.django_db
def test_no_duplicate_project_started_notifications(
    phase_factory, project_factory, user2
):
    """Check that users don't get duplicate notifications if project has multiple phases starting."""
    project = project_factory()

    # Create TWO phases for same project that both start first
    phase_factory(
        module__project=project,
        start_date=timezone.now() - timedelta(hours=12),
        end_date=timezone.now() + timedelta(days=7),
        type="a-phase-type",
    )
    phase_factory(
        module__project=project,
        start_date=timezone.now() - timedelta(hours=12),
        end_date=timezone.now() + timedelta(days=14),
        type="another-phase-type",
    )

    # Make user 2 a follower
    Follow.objects.get_or_create(
        project=project,
        creator=user2,
        defaults={"enabled": True},
    )

    send_recently_started_project_notifications()

    # Should only get ONE notification, not two
    created_notifications = Notification.objects.filter(recipient=user2)
    assert created_notifications.count() == 1

    emails = get_emails_for_address(user2.email)
    assert len(emails) == 1  # Only one email


@pytest.mark.django_db
def test_user_both_follower_and_moderator_gets_one_notification(
    phase_factory, project_factory, user2
):
    """User who is both follower and moderator should get only one notification."""
    project = project_factory()
    project.moderators.add(user2)  # Add as moderator

    phase_factory(
        module__project=project,
        start_date=timezone.now() - timedelta(hours=12),
        end_date=timezone.now() + timedelta(days=7),
    )

    # Also make them a follower
    Follow.objects.get_or_create(
        project=project,
        creator=user2,
        defaults={"enabled": True},
    )

    send_recently_started_project_notifications()

    # Should get ONE notification, not two
    assert Notification.objects.filter(recipient=user2).count() == 1


@pytest.mark.django_db
def test_send_recently_completed_project_notifications(
    phase_factory, project_factory, user2
):
    """Check if notifications are sent for recently completed projects."""
    project = project_factory()

    # Create only one phase for this project so it's the first
    phase_factory(
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
    assert (
        created_notifications.first().notification_type
        == NotificationType.PROJECT_COMPLETED
    )

    follower_emails = get_emails_for_address(user2.email)
    assert len(follower_emails) == 1
    assert project.name.lower() in follower_emails[0].subject.lower()
    assert "has completed" in follower_emails[0].subject.lower()


@pytest.mark.django_db
def test_send_upcoming_event_notifications(
    project_factory, offline_event_factory, user2
):
    project = project_factory()
    offline_event_factory(
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
    assert (
        created_notifications.first().notification_type == NotificationType.EVENT_SOON
    )

    follower_emails = get_emails_for_address(user2.email)
    assert len(follower_emails) == 1
    assert "event in project" in follower_emails[0].subject.lower()
    assert project.name.lower() in follower_emails[0].subject.lower()
