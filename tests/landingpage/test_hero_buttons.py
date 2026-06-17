import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_hero_shows_register_and_account_buttons_for_guests(client):
    response = client.get(reverse("landing_page"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "lp-hero-buttons" in content
    assert "/info/start/" in content
    assert "Register your organization" in content
    assert reverse("account_signup") in content
    assert "Create your Account" in content
    assert "fa-user-plus" in content


@pytest.mark.django_db
def test_hero_shows_only_register_button_for_authenticated_users(client, user):
    client.login(username=user.email, password="password")
    response = client.get(reverse("landing_page"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Register your organization" in content
    assert "/info/start/" in content
    assert reverse("account_signup") not in content
    assert "Create your Account" not in content
