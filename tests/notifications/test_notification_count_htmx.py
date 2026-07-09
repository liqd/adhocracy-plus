import pytest
from django.urls import reverse

from tests.helpers import GuestUserCreator


@pytest.mark.django_db
def test_notification_count_partial_authenticated(client, user):
    url = reverse("notification-count-partial")
    client.login(username=user.email, password="password")
    response = client.get(url, HTTP_HX_REQUEST="true")
    assert response.status_code == 200


@pytest.mark.django_db
def test_notification_count_partial_htmx_after_logout_returns_empty(client, user):
    url = reverse("notification-count-partial")
    client.login(username=user.email, password="password")
    client.logout()
    response = client.get(url, HTTP_HX_REQUEST="true")
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.django_db
def test_notification_count_partial_htmx_anonymous_returns_empty(client):
    url = reverse("notification-count-partial")
    response = client.get(url, HTTP_HX_REQUEST="true")
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.django_db
def test_notification_count_partial_htmx_guest_returns_empty(client):
    url = reverse("notification-count-partial")
    guest = GuestUserCreator().create_guest_user()
    client.force_login(guest)
    response = client.get(url, HTTP_HX_REQUEST="true")
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.django_db
def test_notification_count_partial_non_htmx_anonymous_redirects(client, login_url):
    url = reverse("notification-count-partial")
    response = client.get(url)
    assert response.status_code == 302
    assert login_url in response.url
