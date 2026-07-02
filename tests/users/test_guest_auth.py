import pytest
from django.contrib.auth import authenticate
from django.test import RequestFactory
from django.urls import reverse

from tests.helpers import GuestUserCreator


@pytest.mark.django_db
def test_guest_cannot_be_authenticated_by_identifier_alone():
    guest = GuestUserCreator().create_guest_user()
    request = RequestFactory().get("/")

    assert authenticate(request, username=guest.username, password="wrong") is None
    assert authenticate(request, username=guest.email, password="wrong") is None


@pytest.mark.django_db
def test_guest_cannot_relogin_via_login_form(client):
    guest = GuestUserCreator().create_guest_user()

    for login_value in (guest.username, guest.email):
        response = client.post(
            reverse("account_login"),
            {"login": login_value, "password": "wrong", "remember": ""},
        )
        assert not response.wsgi_request.user.is_authenticated
