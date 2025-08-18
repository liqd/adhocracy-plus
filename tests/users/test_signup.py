import pytest
from django.test import override_settings
from django.urls import reverse

from apps.users.models import User


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
