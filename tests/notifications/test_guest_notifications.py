import pytest
from django.core import mail
from django.urls import reverse

from apps.notifications.models import Notification
from tests.helpers import GuestUserCreator
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_guest_gets_no_notifications(
    module_factory, idea_factory, project_factory, comment_factory, user_factory
):
    """Guest users should not receive any notifications, as they have no
    NotificationSettings and we should not create one as a side effect."""
    project = project_factory(allow_guest_users=True)
    module = module_factory(project=project)
    guest = GuestUserCreator().create_guest_user()
    idea_author = user_factory()
    idea = idea_factory(module=module, creator=guest)

    mail.outbox.clear()
    comment_factory(content_object=idea, creator=idea_author, project=project)

    assert Notification.objects.filter(recipient=guest).count() == 0
    assert len(get_emails_for_address(guest.email)) == 0


@pytest.mark.django_db
def test_guest_cannot_reach_notification_settings(client):
    guest = GuestUserCreator().create_guest_user()
    client.force_login(guest)

    response = client.get(reverse("account_notification_settings"))

    assert response.status_code == 302
    assert response.url != reverse("account_notification_settings")


@pytest.mark.django_db
def test_converted_guest_receives_notification_emails(
    client,
    module_factory,
    idea_factory,
    project_factory,
    comment_factory,
    user_factory,
):
    """A converted guest must get notification emails like any regular user."""
    project = project_factory(allow_guest_users=True)
    module = module_factory(project=project)
    guest = GuestUserCreator().create_guest_user()
    idea = idea_factory(module=module, creator=guest)
    client.force_login(guest)

    response = client.post(
        reverse("guest_convert"),
        {
            "email": "converted@example.com",
            "username": "converteduser",
            "password1": "testpassword123",
            "password2": "testpassword123",
            "terms_of_use": "on",
        },
    )
    assert response.status_code == 302

    # Refresh the in-memory user: idea.creator still points to the stale
    # pre-conversion instance. In production every request loads fresh objects.
    guest.refresh_from_db()

    mail.outbox.clear()
    comment_factory(content_object=idea, creator=user_factory(), project=project)

    assert len(get_emails_for_address("converted@example.com")) == 1
