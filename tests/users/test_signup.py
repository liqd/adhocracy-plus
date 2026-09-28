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
    guest_email = "guest.converted@example.com"

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


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_wizard_renders_first_step(client):
    resp = client.get(reverse("account_signup"))
    assert resp.status_code == 200
    assert resp.context["signup_step"] == 1
    content = resp.content.decode()
    assert 'name="email"' in content
    assert 'name="username"' in content
    assert 'name="password1"' not in content
    assert "signup-wizard" in content


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_wizard_step1_advances_to_step2(client):
    resp = client.post(
        reverse("account_signup"),
        {
            "signup_step": "1",
            "email": "wizard@example.com",
            "username": "wizarduser",
        },
        HTTP_HX_REQUEST="true",
    )
    assert resp.status_code == 200
    assert resp.context["signup_step"] == 2
    assert 'name="password1"' in resp.content.decode()
    session_data = client.session["signup_wizard"]
    assert session_data["email"] == "wizard@example.com"
    assert session_data["username"] == "wizarduser"


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_wizard_step1_shows_errors(client):
    resp = client.post(
        reverse("account_signup"),
        {"signup_step": "1", "email": "not-an-email", "username": "wu"},
        HTTP_HX_REQUEST="true",
    )
    assert resp.status_code == 200
    assert resp.context["signup_step"] == 1
    assert resp.context["step_form"].errors
    assert "signup_wizard" not in client.session


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_wizard_step2_advances_to_step3(client):
    client.post(
        reverse("account_signup"),
        {"signup_step": "1", "email": "wizard@example.com", "username": "wizarduser"},
        HTTP_HX_REQUEST="true",
    )
    resp = client.post(
        reverse("account_signup"),
        {"signup_step": "2", "password1": "password", "password2": "password"},
        HTTP_HX_REQUEST="true",
    )
    assert resp.status_code == 200
    assert resp.context["signup_step"] == 3
    content = resp.content.decode()
    assert 'name="terms_of_use"' in content
    assert 'name="password1"' not in content
    assert client.session["signup_wizard"]["password1"] == "password"


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_wizard_completes_registration(client):
    client.post(
        reverse("account_signup"),
        {"signup_step": "1", "email": "wizard@example.com", "username": "wizarduser"},
        HTTP_HX_REQUEST="true",
    )
    client.post(
        reverse("account_signup"),
        {"signup_step": "2", "password1": "password", "password2": "password"},
        HTTP_HX_REQUEST="true",
    )
    resp = client.post(
        reverse("account_signup"),
        {"signup_step": "3", "terms_of_use": "on", "get_newsletters": "on"},
    )
    assert resp.status_code == 302
    user = User.objects.get(username="wizarduser")
    assert user.email == "wizard@example.com"
    assert user.check_password("password")
    assert user.get_newsletters
    assert "signup_wizard" not in client.session


@override_settings(CAPTCHA=False)
@pytest.mark.django_db
def test_signup_wizard_step2_back_button_reads_session(client):
    client.post(
        reverse("account_signup"),
        {"signup_step": "1", "email": "wizard@example.com", "username": "wizarduser"},
        HTTP_HX_REQUEST="true",
    )
    resp = client.get(reverse("account_signup") + "?step=1", HTTP_HX_REQUEST="true")
    assert resp.status_code == 200
    assert resp.context["signup_step"] == 1
    assert resp.context["step_form"]["email"].value() == "wizard@example.com"
