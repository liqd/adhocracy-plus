import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_required(client, login_url, organisation):
    url = reverse(
        "a4dashboard:project-moderation",
        kwargs={"organisation_slug": organisation.slug},
    )
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == login_url + "?next=" + url


@pytest.mark.django_db
def test_moderator_can_view_dashboard_moderation(client, project_factory):
    project = project_factory()
    moderator = project.moderators.first()
    organisation = project.organisation
    client.login(username=moderator.email, password="password")

    url = reverse(
        "a4dashboard:project-moderation",
        kwargs={"organisation_slug": organisation.slug},
    )
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name[0] == "a4_candy_dashboard/moderation_dashboard.html"
    assert "project_api_url" in response.context_data
    expected_url = (
        reverse("moderationprojects-list") + f"?organisation={organisation.slug}"
    )
    assert response.context_data["project_api_url"] == expected_url


@pytest.mark.django_db
def test_normal_user_cannot_view_dashboard_moderation(client, user, organisation):
    client.login(username=user.email, password="password")
    url = reverse(
        "a4dashboard:project-moderation",
        kwargs={"organisation_slug": organisation.slug},
    )
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_of_other_organisation_cannot_view_dashboard_moderation(
    client, project_factory, organisation_factory
):
    project = project_factory()
    moderator = project.moderators.first()
    other_organisation = organisation_factory()
    client.login(username=moderator.email, password="password")

    url = reverse(
        "a4dashboard:project-moderation",
        kwargs={"organisation_slug": other_organisation.slug},
    )
    response = client.get(url)

    assert response.status_code == 403
