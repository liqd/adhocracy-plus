import pytest
from django.test import override_settings
from django.urls import reverse

from apps.users.models import User
from tests.helpers import GuestUserCreator
from tests.helpers import get_emails_for_address


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_user_newsletter_checked(client):
    resp = client.post(
        reverse("account_signup"),
        {
            "username": "dauser",
            "email": "mail@example.com",
            "get_newsletters": "on",
            "password1": "password",
            "password2": "password",
            "terms_of_use": "on",
        },
    )
    assert resp.status_code == 302
    user = User.objects.get()
    assert user.get_newsletters


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_user_newsletter_not_checked(client):
    resp = client.post(
        reverse("account_signup"),
        {
            "username": "dauser",
            "email": "mail@example.com",
            "password1": "password",
            "password2": "password",
            "terms_of_use": "on",
        },
    )
    assert resp.status_code == 302
    user = User.objects.get()
    assert not user.get_newsletters


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_user_unchecked_terms_of_use(client):
    resp = client.post(
        reverse("account_signup"),
        {
            "username": "dauser",
            "email": "mail@example.com",
            "password1": "password",
            "password2": "password",
        },
    )
    assert User.objects.count() == 0
    assert not resp.context["form"].is_valid()
    assert list(resp.context["form"].errors.keys()) == ["terms_of_use"]


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_bot_trap_deactivates_user(client):
    resp = client.post(
        reverse("account_signup"),
        {
            "username": "botuser",
            "email": "bot@example.com",
            "password1": "password",
            "password2": "password",
            "terms_of_use": "on",
            "accept_marketing_partners": "on",
        },
    )
    assert resp.status_code == 302
    user = User.objects.get(username="botuser")
    assert not user.is_active


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_without_bot_trap_creates_active_user(client):
    resp = client.post(
        reverse("account_signup"),
        {
            "username": "realuser",
            "email": "real@example.com",
            "password1": "password",
            "password2": "password",
            "terms_of_use": "on",
        },
    )
    assert resp.status_code == 302
    user = User.objects.get(username="realuser")
    assert user.is_active


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_convert_guest_user(client):
    guest_user_creator = GuestUserCreator()
    guest_user = guest_user_creator.create_guest_user()
    client.force_login(guest_user)
    guest_email = "mail@example.com"

    response = client.post(
        reverse("guest_convert"),
        data={
            "username": "aguestuser",
            "email": guest_email,
            "password1": "password",
            "password2": "password",
            "terms_of_use": "on",
        },
    )

    assert response.status_code == 302

    user_emails = get_emails_for_address(guest_email)
    assert len(user_emails) == 1
    subject = user_emails[0].subject
    assert subject.startswith(
        "Please confirm your registration on"
    ) or subject.startswith("Bitte bestätigen Sie Ihre Registrierung auf")
