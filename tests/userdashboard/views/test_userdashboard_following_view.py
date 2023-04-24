import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_required(client, login_url):
    url = reverse("userdashboard-following")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == login_url + "?next=" + url


@pytest.mark.django_db
def test_normal_user_can_view_userdashboard_following(client, user):
    client.login(username=user.email, password="password")
    url = reverse("userdashboard-following")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_userdashboard_following_context_data(client, user, idea_factory):
    client.login(username=user.email, password="password")
    url = reverse("userdashboard-following")
    response = client.get(url)
    assert response.status_code == 200
    assert (
        response.template_name[0]
        == "a4_candy_userdashboard/userdashboard_following.html"
    )

    context_data = response.context_data
    assert len(context_data["view"].projects) == 0

    idea = idea_factory(creator=user)
    response2 = client.get(url)

    context_data_new = response2.context_data
    assert idea.project in context_data_new["view"].projects
