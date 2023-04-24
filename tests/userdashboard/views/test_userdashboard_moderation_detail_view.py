import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_required(client, login_url, project_factory):
    project = project_factory()
    url = reverse("userdashboard-moderation-detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == login_url + "?next=" + url


@pytest.mark.django_db
def test_moderator_can_view_moderation_detail_dashboard(client, project_factory):
    project = project_factory()
    moderator = project.moderators.first()
    client.login(username=moderator.email, password="password")
    url = reverse("userdashboard-moderation-detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.status_code == 200
    assert (
        response.template_name[0]
        == "a4_candy_userdashboard/userdashboard_moderation_detail.html"
    )


@pytest.mark.django_db
def test_wrong_moderator_cannot_view_moderation_detail_dashboard(
    client, project_factory
):
    project_1 = project_factory()
    project_2 = project_factory()
    moderator = project_1.moderators.first()
    client.login(username=moderator.email, password="password")
    url = reverse("userdashboard-moderation-detail", kwargs={"slug": project_2.slug})
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_normal_user_cannot_view_moderation_dashboard(client, user, project_factory):
    project = project_factory()
    client.login(username=user.email, password="password")
    url = reverse("userdashboard-moderation-detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderation_dashboard_context_data(client, project_factory):
    project = project_factory()
    moderator = project.moderators.first()
    client.login(username=moderator.email, password="password")
    url = reverse("userdashboard-moderation-detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.status_code == 200
    assert (
        response.template_name[0]
        == "a4_candy_userdashboard/userdashboard_moderation_detail.html"
    )

    context_data = response.context_data
    moderation_comments_api_url = reverse(
        "moderationcomments-list", kwargs={"project_pk": project.pk}
    )
    assert "moderation_comments_api_url" in context_data
    assert moderation_comments_api_url == context_data["moderation_comments_api_url"]
    assert context_data["view"].project == project
    assert context_data["view"].project_url == project.get_absolute_url()
