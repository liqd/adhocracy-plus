import pytest
from django.urls import reverse

from tests.mapideas.factories import MapIdeaFactory


def _items_url(project):
    return reverse("moderationitems-list", kwargs={"project_pk": project.pk})


def _idea_url(project, idea, basename="moderationideas"):
    return reverse(
        basename + "-detail", kwargs={"project_pk": project.pk, "pk": idea.pk}
    )


def _login_moderator(apiclient, project):
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")


@pytest.mark.django_db
def test_idea_is_unread_by_default_with_api_url(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)

    response = apiclient.get(_items_url(project) + "?content_type=ideas")

    assert response.status_code == 200
    idea_item = next(item for item in response.data if item["item_type"] == "idea")
    assert idea_item["is_unread"] is True
    assert idea_item["api_url"] == _idea_url(project, idea)


@pytest.mark.django_db
def test_map_idea_uses_map_idea_api_url(apiclient, idea):
    map_idea = MapIdeaFactory(module=idea.module)
    project = idea.project
    _login_moderator(apiclient, project)

    response = apiclient.get(_items_url(project) + "?content_type=ideas")

    map_item = next(item for item in response.data if item["title"] == map_idea.name)
    assert map_item["api_url"] == _idea_url(project, map_idea, "moderationmapideas")


@pytest.mark.django_db
def test_mark_idea_read_and_unread(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)
    url = _idea_url(project, idea)

    response = apiclient.get(url + "mark_read/")
    assert response.status_code == 200
    assert response.data["is_unread"] is False
    idea.refresh_from_db()
    assert idea.is_reviewed is True

    response = apiclient.get(url + "mark_unread/")
    assert response.status_code == 200
    assert response.data["is_unread"] is True
    idea.refresh_from_db()
    assert idea.is_reviewed is False


@pytest.mark.django_db
def test_mark_map_idea_read(apiclient, idea):
    map_idea = MapIdeaFactory(module=idea.module)
    project = idea.project
    _login_moderator(apiclient, project)
    url = _idea_url(project, map_idea, "moderationmapideas")

    response = apiclient.get(url + "mark_read/")

    assert response.status_code == 200
    map_idea.refresh_from_db()
    assert map_idea.is_reviewed is True


@pytest.mark.django_db
def test_is_reviewed_filter_applies_to_ideas(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)
    idea.is_reviewed = True
    idea.save(ignore_modified=True)

    response = apiclient.get(
        _items_url(project) + "?content_type=ideas&is_reviewed=false"
    )
    assert [item["item_type"] for item in response.data] == []

    response = apiclient.get(
        _items_url(project) + "?content_type=ideas&is_reviewed=all"
    )
    assert [item["pk"] for item in response.data] == [idea.pk]


@pytest.mark.django_db
def test_wrong_moderator_cannot_mark_idea_read(apiclient, idea, project_factory):
    other_project = project_factory()
    other_moderator = other_project.moderators.first()
    apiclient.login(username=other_moderator.email, password="password")

    response = apiclient.get(_idea_url(idea.project, idea) + "mark_read/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_idea_status_and_official_feedback(apiclient, idea, moderator_feedback):
    moderator_feedback.feedback_text = "<p>Great idea</p>"
    moderator_feedback.save()
    idea.moderator_status = "ACCEPTED"
    idea.moderator_feedback_text = moderator_feedback
    idea.save(ignore_modified=True)
    project = idea.project
    _login_moderator(apiclient, project)

    response = apiclient.get(_items_url(project) + "?content_type=ideas")

    idea_item = next(item for item in response.data if item["item_type"] == "idea")
    assert idea_item["moderator_status"] == "ACCEPTED"
    assert idea_item["moderator_status_display"] == "Accepted"
    assert idea_item["moderator_feedback_text"] == "Great idea"
