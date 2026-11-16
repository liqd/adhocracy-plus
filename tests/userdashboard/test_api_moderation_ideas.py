import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from apps.moderatorfeedback.models import ModeratorFeedback
from tests.mapideas.factories import MapIdeaFactory


def _items_url(project):
    return reverse("moderationitems-list", kwargs={"project_pk": project.pk})


def _idea_url(project, idea, basename="moderationideas"):
    return reverse(
        basename + "-detail", kwargs={"project_pk": project.pk, "pk": idea.pk}
    )


def _feedback_url(project, idea, basename="moderationideas"):
    return reverse(
        basename + "-feedback", kwargs={"project_pk": project.pk, "pk": idea.pk}
    )


def _idea_item(apiclient, project, idea):
    response = apiclient.get(_items_url(project) + "?content_type=ideas")
    return next(item for item in response.data if item["pk"] == idea.pk)


def _uploaded_png(name="test.png"):
    file = io.BytesIO()
    Image.new("RGBA", size=(600, 600), color=(155, 0, 0)).save(file, format="PNG")
    return SimpleUploadedFile(name, file.getvalue(), content_type="image/png")


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


@pytest.mark.django_db
def test_idea_renders_html_and_truncates_long_text(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)
    idea.description = (
        "<p>A <strong>bold</strong> idea with " + ("word " * 200) + "</p>"
    )
    idea.save(ignore_modified=True)

    item = _idea_item(apiclient, project, idea)

    assert item["text"] == idea.description
    assert item["text_preview"]
    assert len(item["text_preview"]) < len(item["text"])
    assert item["text_preview"].endswith("…</p>")
    assert item["image"] is None


@pytest.mark.django_db
def test_short_idea_text_has_no_preview(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)
    idea.description = "<p>Short <strong>formatted</strong> idea</p>"
    idea.save(ignore_modified=True)

    item = _idea_item(apiclient, project, idea)

    assert item["text"] == "<p>Short <strong>formatted</strong> idea</p>"
    assert item["text_preview"] is None


@pytest.mark.django_db
def test_idea_image_urls(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)
    idea.image = _uploaded_png()
    idea.save(ignore_modified=True)

    item = _idea_item(apiclient, project, idea)

    assert item["image"]["thumbnail"]
    assert item["image"]["full"]
    assert item["image"]["thumbnail"] != item["image"]["full"]


@pytest.mark.django_db
def test_map_idea_has_feedback_api_url(apiclient, idea):
    map_idea = MapIdeaFactory(module=idea.module)
    project = idea.project
    _login_moderator(apiclient, project)

    item = _idea_item(apiclient, project, map_idea)

    assert item["feedback_api_url"] == _feedback_url(
        project, map_idea, "moderationmapideas"
    )


@pytest.mark.django_db
def test_moderator_can_set_idea_status(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)
    url = _idea_url(project, idea)

    response = apiclient.patch(url, {"moderator_status": "ACCEPTED"}, format="json")

    assert response.status_code == 200
    idea.refresh_from_db()
    assert idea.moderator_status == "ACCEPTED"
    assert idea.is_reviewed is True


@pytest.mark.django_db
def test_moderator_can_create_update_and_delete_idea_feedback(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)
    url = _feedback_url(project, idea)

    response = apiclient.get(url)
    assert response.status_code == 200
    assert response.data is None

    response = apiclient.post(url, {"feedback_text": "<p>Nice idea</p>"}, format="json")
    assert response.status_code == 201
    feedback_pk = response.data["pk"]
    assert response.data["feedback_text"] == "<p>Nice idea</p>"

    idea.refresh_from_db()
    assert idea.moderator_feedback_text_id == feedback_pk
    assert idea.is_reviewed is True

    response = apiclient.get(url)
    assert response.data["pk"] == feedback_pk

    response = apiclient.put(
        url, {"feedback_text": "<p>Updated feedback</p>"}, format="json"
    )
    assert response.status_code == 200
    assert response.data["feedback_text"] == "<p>Updated feedback</p>"

    response = apiclient.delete(url)
    assert response.status_code == 204
    idea.refresh_from_db()
    assert idea.moderator_feedback_text is None
    assert not ModeratorFeedback.objects.filter(pk=feedback_pk).exists()


@pytest.mark.django_db
def test_posting_feedback_twice_updates_the_existing_feedback(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)
    url = _feedback_url(project, idea)

    response = apiclient.post(url, {"feedback_text": "<p>First</p>"}, format="json")
    feedback_pk = response.data["pk"]

    response = apiclient.post(url, {"feedback_text": "<p>Second</p>"}, format="json")

    assert response.status_code == 200
    assert response.data["pk"] == feedback_pk
    assert response.data["feedback_text"] == "<p>Second</p>"
    assert ModeratorFeedback.objects.count() == 1
    idea.refresh_from_db()
    assert idea.moderator_feedback_text_id == feedback_pk


@pytest.mark.django_db
def test_status_can_be_set_with_feedback_and_cleared(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)
    url = _feedback_url(project, idea)

    response = apiclient.post(
        url,
        {"feedback_text": "<p>Feedback</p>", "moderator_status": "ACCEPTED"},
        format="json",
    )

    assert response.status_code == 201
    idea.refresh_from_db()
    assert idea.moderator_status == "ACCEPTED"

    response = apiclient.patch(
        _idea_url(project, idea), {"moderator_status": None}, format="json"
    )

    assert response.status_code == 200
    idea.refresh_from_db()
    assert idea.moderator_status is None


@pytest.mark.django_db
def test_non_moderator_cannot_write_idea_feedback(
    apiclient, idea, user, moderator_feedback
):
    apiclient.force_authenticate(user=user)
    url = _feedback_url(idea.project, idea)

    response = apiclient.post(
        url,
        {"feedback_text": "not allowed"},
        format="json",
    )

    assert response.status_code == 403

    idea.moderator_feedback_text = moderator_feedback
    idea.save(ignore_modified=True)

    response = apiclient.delete(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_idea_feedback_without_mark_resolved_keeps_idea_unread(apiclient, idea):
    project = idea.project
    _login_moderator(apiclient, project)

    response = apiclient.post(
        _feedback_url(project, idea),
        {"feedback_text": "<p>Feedback</p>", "mark_resolved": False},
        format="json",
    )

    assert response.status_code == 201
    idea.refresh_from_db()
    assert idea.is_reviewed is False
