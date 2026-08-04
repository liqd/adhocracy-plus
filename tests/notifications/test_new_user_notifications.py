from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone

from adhocracy4.follows.models import Follow
from apps.notifications.models import NotificationSettings
from apps.notifications.services import NotificationService
from apps.notifications.strategies import ProjectInvitationCreated
from apps.notifications.tasks import send_recently_started_project_notifications
from apps.projects.models import ParticipantInvite


@pytest.mark.django_db
def test_new_user_without_settings_gets_project_started_email(
    project_factory, phase_factory, user_factory
):
    project = project_factory()
    phase_factory(
        module__project=project,
        start_date=timezone.now() - timedelta(hours=12),
        end_date=timezone.now() + timedelta(days=7),
    )
    user = user_factory()
    # Simulate a user that was created before notification settings existed
    NotificationSettings.objects.filter(user=user).delete()
    assert not NotificationSettings.objects.filter(user=user).exists()

    Follow.objects.get_or_create(
        project=project, creator=user, defaults={"enabled": True}
    )

    mail.outbox.clear()
    send_recently_started_project_notifications()

    settings = NotificationSettings.objects.get(user=user)
    assert settings.email_project_updates is True
    assert len([m for m in mail.outbox if user.email in m.to]) == 1


@pytest.mark.django_db
def test_new_user_without_settings_gets_project_invitation_email(
    project_factory, user_factory
):
    project = project_factory()
    user = user_factory()
    NotificationSettings.objects.filter(user=user).delete()
    assert not NotificationSettings.objects.filter(user=user).exists()

    invite = ParticipantInvite.objects.create(
        project=project,
        creator=user_factory(),
        email=user.email,
        site="example.com",
    )

    mail.outbox.clear()
    NotificationService.create_notifications(invite, ProjectInvitationCreated())

    assert NotificationSettings.objects.filter(user=user).exists()
    assert len([m for m in mail.outbox if user.email in m.to]) == 1
