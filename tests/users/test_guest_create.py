import pytest
from django.core.cache import cache
from django.core.validators import validate_email
from django.test import override_settings
from django.urls import reverse
from django.utils import translation
from guest_user.models import Guest

from apps.users.guest_username_words import GUEST_USERNAME_ADJECTIVES_DE
from apps.users.models import User
from apps.users.utils import generate_guest_username


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_create_form_prefills_unique_username(client):
    response = client.get(reverse("guest_create"))

    assert response.status_code == 200
    initial = response.context["form"].fields["username"].initial
    assert initial
    assert len(initial) >= 5
    assert not User.objects.filter(username__iexact=initial).exists()
    assert b'name="username"' in response.content
    assert b'for="id_username"' in response.content
    assert reverse("guest_username_check").encode() in response.content
    assert b'id="guest-username-feedback"' in response.content


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_create_uses_chosen_username(client):
    response = client.post(
        reverse("guest_create"),
        {"username": "Curious Citizen", "terms_of_use": "on"},
    )

    assert response.status_code == 302
    assert Guest.objects.count() == 1
    user = User.objects.get()
    assert user.username == "Curious Citizen"
    assert client.session["_auth_user_id"] == str(user.pk)


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_create_rejects_taken_username(client, user):
    response = client.post(
        reverse("guest_create"),
        {"username": user.username, "terms_of_use": "on"},
    )

    assert response.status_code == 200
    assert "username" in response.context["form"].errors
    assert Guest.objects.count() == 0


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_create_rejects_short_username(client):
    response = client.post(
        reverse("guest_create"),
        {"username": "abc", "terms_of_use": "on"},
    )

    assert response.status_code == 200
    assert "username" in response.context["form"].errors
    assert Guest.objects.count() == 0


@pytest.mark.django_db
def test_generate_guest_username_skips_existing_names(user):
    taken = user.username
    for _ in range(25):
        username = generate_guest_username()
        assert username != taken
        assert not User.objects.filter(username__iexact=username).exists()


@pytest.mark.django_db
def test_generate_guest_username_uses_active_language():
    with translation.override("de"):
        username = generate_guest_username()
    assert username.split(" ")[0] in GUEST_USERNAME_ADJECTIVES_DE
    assert ":" in username


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_create_sanitizes_placeholder_email(client):
    response = client.post(
        reverse("guest_create"),
        {"username": "Neugierige:r Bürger:in", "terms_of_use": "on"},
    )

    assert response.status_code == 302
    user = User.objects.get()
    assert user.username == "Neugierige:r Bürger:in"
    assert user.email == "guest+Neugierige_r_Buerger_in@liqd.net"
    validate_email(user.email)


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_create_sanitizes_placeholder_email_with_at_sign(client):
    response = client.post(
        reverse("guest_create"),
        {"username": "foo@bar", "terms_of_use": "on"},
    )

    assert response.status_code == 302
    user = User.objects.get()
    assert user.email == "guest+foo_bar@liqd.net"
    validate_email(user.email)


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_create_keeps_placeholder_email_unique(client):
    client.post(
        reverse("guest_create"),
        {"username": "Max Mustermann", "terms_of_use": "on"},
    )
    client.logout()
    client.post(
        reverse("guest_create"),
        {"username": "Max_Mustermann", "terms_of_use": "on"},
    )

    emails = set(User.objects.values_list("email", flat=True))
    assert emails == {
        "guest+Max_Mustermann@liqd.net",
        "guest+Max_Mustermann1@liqd.net",
    }


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_username_check_available(client):
    response = client.get(reverse("guest_username_check"), {"username": "Unique Guest"})

    assert response.status_code == 200
    assert response.context["status"] == "ok"
    assert response.content.decode().strip()


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_username_check_taken(client, user):
    response = client.get(reverse("guest_username_check"), {"username": user.username})

    assert response.status_code == 200
    assert response.context["status"] == "error"


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_username_check_too_short(client):
    response = client.get(reverse("guest_username_check"), {"username": "ab"})

    assert response.status_code == 200
    assert response.context["status"] == "error"


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_guest_username_check_empty_returns_no_feedback(client):
    response = client.get(reverse("guest_username_check"), {"username": ""})

    assert response.status_code == 200
    assert response.content.decode().strip() == ""


@override_settings(
    CAPTCHA=False, ACCOUNT_RATE_LIMITS={"guest_username_check": "2/m/ip"}
)
@pytest.mark.django_db
def test_guest_username_check_is_rate_limited(client):
    cache.clear()
    try:
        for _ in range(2):
            response = client.get(
                reverse("guest_username_check"), {"username": "Unique Guest"}
            )
            assert response.status_code == 200

        response = client.get(
            reverse("guest_username_check"), {"username": "Unique Guest"}
        )
        assert response.status_code == 429
    finally:
        cache.clear()
