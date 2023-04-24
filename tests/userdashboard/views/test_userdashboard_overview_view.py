import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_required(client, login_url):
    url = reverse("userdashboard-overview")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == login_url + "?next=" + url


@pytest.mark.django_db
def test_normal_user_can_view_userdashboard_overview(client, user):
    client.login(username=user.email, password="password")
    url = reverse("userdashboard-overview")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_userdashboard_overview_context_data(
    client, user, user2, idea_factory, comment_factory
):
    client.login(username=user.email, password="password")
    url = reverse("userdashboard-overview")
    response = client.get(url)
    assert response.status_code == 200
    assert (
        response.template_name[0]
        == "a4_candy_userdashboard/userdashboard_overview.html"
    )

    context_data = response.context_data
    assert len(context_data["view"].organisations) == 0
    assert len(context_data["view"].projects) == 0
    assert len(context_data["view"].actions) == 0

    idea = idea_factory(creator=user)
    comment = comment_factory(content_object=idea, creator=user2)
    response2 = client.get(url)

    context_data_new = response2.context_data
    assert idea.project in context_data_new["view"].projects
    assert idea.project.organisation in context_data_new["view"].organisations
    assert len(context_data_new["view"].actions) == 1
    assert context_data_new["view"].actions[0].actor == user2
    assert context_data_new["view"].actions[0].target == idea
    assert context_data_new["view"].actions[0].obj == comment
