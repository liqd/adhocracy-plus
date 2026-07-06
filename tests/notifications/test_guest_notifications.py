import pytest
from django.core import mail
from django.urls import reverse

from apps.notifications.models import Notification
from tests.helpers import GuestUserCreator
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_guest_gets_in_app_notification_but_no_email(
    module_factory, idea_factory, project_factory, comment_factory, user_factory
):
    project = project_factory(allow_guest_users=True)
    module = module_factory(project=project)
    guest = GuestUserCreator().create_guest_user()
    idea_author = user_factory()
    idea = idea_factory(module=module, creator=guest)

    mail.outbox.clear()
    comment_factory(content_object=idea, creator=idea_author, project=project)

    assert Notification.objects.filter(recipient=guest).count() == 1
    assert len(get_emails_for_address(guest.email)) == 0


@pytest.mark.django_db
def test_guest_cannot_reach_notification_settings(client):
    guest = GuestUserCreator().create_guest_user()
    client.force_login(guest)

    response = client.get(reverse("account_notification_settings"))

    assert response.status_code == 302
    assert response.url != reverse("account_notification_settings")
