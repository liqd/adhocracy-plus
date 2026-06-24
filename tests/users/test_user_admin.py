import pytest
from django.contrib import auth
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from guest_user.functions import get_guest_model
from guest_user.functions import is_guest_user

from tests.helpers import GuestUserCreator

User = auth.get_user_model()
GuestUser = get_guest_model()


@pytest.mark.django_db
def test_admin_can_access_guest_user(client, admin):
    guest_user_creator = GuestUserCreator()
    guest_user = guest_user_creator.create_guest_user()
    assert is_guest_user(guest_user)

    client.logout()

    if hasattr(client, "session"):
        client.session.flush()

    response = client.get("/")
    assert isinstance(response.wsgi_request.user, AnonymousUser)

    if hasattr(client, "session"):
        assert not client.session.session_key

    url = reverse("admin:a4_candy_users_user_change", args=[guest_user.pk])
    client.force_login(admin)
    response = client.get(url)
    assert response.status_code == 200
