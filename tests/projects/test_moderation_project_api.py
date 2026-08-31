import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_moderator_can_list_moderated_projects(apiclient, project_factory, user):
    project_1 = project_factory()
    project_2 = project_factory()
    user.project_moderator.add(project_1, project_2)

    apiclient.login(username=user.email, password="password")
    url = reverse("moderationprojects-list")
    response = apiclient.get(url)

    assert response.status_code == 200
    assert len(response.data) == 2
    titles = [project["title"] for project in response.data]
    assert project_1.name in titles
    assert project_2.name in titles


@pytest.mark.django_db
def test_filter_by_organisation(apiclient, project_factory, organisation_factory, user):
    organisation_1 = organisation_factory()
    organisation_2 = organisation_factory()
    project_1 = project_factory(organisation=organisation_1)
    project_2 = project_factory(organisation=organisation_2)
    user.project_moderator.add(project_1, project_2)

    apiclient.login(username=user.email, password="password")
    url = reverse("moderationprojects-list")
    response = apiclient.get(url, {"organisation": organisation_1.slug})

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == project_1.name


@pytest.mark.django_db
def test_anonymous_cannot_access_moderation_projects(apiclient):
    url = reverse("moderationprojects-list")
    response = apiclient.get(url)
    assert response.status_code in (401, 403)
