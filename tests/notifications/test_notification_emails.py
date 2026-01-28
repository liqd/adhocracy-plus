from datetime import timedelta

import pytest
from django.utils import timezone

from adhocracy4.follows.models import Follow
from apps.notifications.tasks import send_recently_started_project_notifications
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_send_recently_started_project_notifications_multilingual(
    phase_factory, project_factory, user2, user
):
    """Check notifications are sent in correct language per user."""
    project = project_factory()

    phase_factory(
        module__project=project,
        start_date=timezone.now() - timedelta(hours=12),
        end_date=timezone.now() + timedelta(days=7),
    )

    # User2 prefers English
    user2.language = "en"
    user2.save()
    Follow.objects.get_or_create(
        project=project, creator=user2, defaults={"enabled": True}
    )

    # user prefers German
    user.language = "de"
    user.save()
    Follow.objects.get_or_create(
        project=project, creator=user, defaults={"enabled": True}
    )

    send_recently_started_project_notifications()

    # Check English email
    email_en = get_emails_for_address(user2.email)[0]
    assert project.name.lower() in email_en.subject.lower()
    assert "starts now!" in email_en.subject.lower()

    # Check German email
    email_de = get_emails_for_address(user.email)[0]
    assert project.name.lower() in email_de.subject.lower()
    assert "beginnt jetzt!" in email_de.subject.lower()
