from datetime import timedelta

import pytest
from django.urls import reverse

from tests.mapideas.factories import MapIdeaFactory


def _url(project):
    return reverse("moderationitems-list", kwargs={"project_pk": project.pk})


@pytest.mark.django_db
def test_anonymous_cannot_view_moderation_items(apiclient, project):
    response = apiclient.get(_url(project))
    assert response.status_code == 403


@pytest.mark.django_db
def test_wrong_moderator_cannot_view_moderation_items(apiclient, project_factory):
    project_1 = project_factory()
    project_2 = project_factory()

    moderator = project_1.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    response = apiclient.get(_url(project_2))
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_sees_comments_and_ideas(apiclient, comment_factory, idea):
    comment_factory(content_object=idea)
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    response = apiclient.get(_url(project))
    assert response.status_code == 200
    item_types = [item["item_type"] for item in response.data]
    assert "comment" in item_types
    assert "idea" in item_types

    idea_item = next(item for item in response.data if item["item_type"] == "idea")
    comment_item = next(
        item for item in response.data if item["item_type"] == "comment"
    )
    assert idea_item["label"] == "Idea"
    assert comment_item["label"] == "Comment"
    assert idea_item["title"] == idea.name
    assert idea_item["url"] == idea.get_absolute_url()
    assert idea_item["moderate_url"] != ""
    assert comment_item["api_url"] != ""


@pytest.mark.django_db
def test_map_ideas_are_included(apiclient, idea):
    map_idea = MapIdeaFactory(module=idea.module)
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    response = apiclient.get(_url(project) + "?content_type=ideas")
    assert response.status_code == 200
    assert map_idea.pk in [item["pk"] for item in response.data]


@pytest.mark.django_db
def test_filter_by_content_type(apiclient, comment_factory, idea):
    comment_factory(content_object=idea)
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    response = apiclient.get(_url(project) + "?content_type=ideas")
    assert response.status_code == 200
    assert [item["item_type"] for item in response.data] == ["idea"]

    response = apiclient.get(_url(project) + "?content_type=comments")
    assert response.status_code == 200
    assert [item["item_type"] for item in response.data] == ["comment"]


@pytest.mark.django_db
def test_is_reviewed_filter_applies_to_comments_only(apiclient, comment_factory, idea):
    reviewed_comment = comment_factory(content_object=idea, is_reviewed=True)
    unread_comment = comment_factory(content_object=idea, is_reviewed=False)
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    response = apiclient.get(_url(project) + "?is_reviewed=false")
    assert response.status_code == 200
    comment_pks = [
        item["pk"] for item in response.data if item["item_type"] == "comment"
    ]
    assert unread_comment.pk in comment_pks
    assert reviewed_comment.pk not in comment_pks
    assert any(item["item_type"] == "idea" for item in response.data)


@pytest.mark.django_db
def test_ordering_by_created(apiclient, comment_factory, idea):
    comment_1 = comment_factory(content_object=idea)
    comment_2 = comment_factory(
        content_object=idea, created=comment_1.created + timedelta(hours=1)
    )
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    response = apiclient.get(
        _url(project) + "?content_type=comments&is_reviewed=all&ordering=-created"
    )
    assert response.status_code == 200
    assert [item["pk"] for item in response.data] == [comment_2.pk, comment_1.pk]
