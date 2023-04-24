import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_required(client, login_url):
    url = reverse("userdashboard-moderation")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == login_url + "?next=" + url


@pytest.mark.django_db
def test_moderator_can_view_moderation_dashboard(client, project_factory):
    project = project_factory()
    moderator = project.moderators.first()
    client.login(username=moderator.email, password="password")
    url = reverse("userdashboard-moderation")
    response = client.get(url)
    assert response.status_code == 200
    assert (
        response.template_name[0]
        == "a4_candy_userdashboard/userdashboard_moderation.html"
    )


@pytest.mark.django_db
def test_normal_user_cannot_view_moderation_dashboard(client, user):
    client.login(username=user.email, password="password")
    url = reverse("userdashboard-moderation")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderation_dashboard_context_data(client, project_factory):
    project = project_factory()
    moderator = project.moderators.first()
    client.login(username=moderator.email, password="password")
    url = reverse("userdashboard-moderation")
    response = client.get(url)
    assert response.status_code == 200
    assert (
        response.template_name[0]
        == "a4_candy_userdashboard/userdashboard_moderation.html"
    )

    context_data = response.context_data
    assert project.organisation in context_data["view"].organisations
