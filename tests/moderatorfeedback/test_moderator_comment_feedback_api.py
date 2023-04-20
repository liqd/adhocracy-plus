import pytest
from django.urls import reverse

from apps.moderatorfeedback.models import ModeratorCommentFeedback


@pytest.mark.django_db
def test_anonymous_cannot_add_feedback(apiclient, idea, comment_factory):
    comment = comment_factory(pk=1, content_object=idea)

    assert ModeratorCommentFeedback.objects.all().count() == 0
    url = reverse("moderatorfeedback-list", kwargs={"comment_pk": comment.pk})
    data = {"feedback_text": "a statement"}
    response = apiclient.post(url, data)
    assert response.status_code == 403
    assert ModeratorCommentFeedback.objects.all().count() == 0


@pytest.mark.django_db
def test_user_cannot_add_feedback(apiclient, idea, user, comment_factory):
    comment = comment_factory(pk=1, content_object=idea)

    assert ModeratorCommentFeedback.objects.all().count() == 0
    url = reverse("moderatorfeedback-list", kwargs={"comment_pk": comment.pk})
    data = {"feedback_text": "a statement"}
    apiclient.force_authenticate(user=user)
    response = apiclient.post(url, data)
    assert response.status_code == 403
    assert ModeratorCommentFeedback.objects.all().count() == 0


@pytest.mark.django_db
def test_moderator_can_add_feedback(apiclient, idea, user, comment_factory):
    comment = comment_factory(pk=1, content_object=idea)
    idea.project.moderators.add(user)

    assert ModeratorCommentFeedback.objects.all().count() == 0
    url = reverse("moderatorfeedback-list", kwargs={"comment_pk": comment.pk})
    data = {"feedback_text": "a statement"}
    apiclient.force_authenticate(user=user)
    response = apiclient.post(url, data)
    assert response.status_code == 201
    assert ModeratorCommentFeedback.objects.all().count() == 1


@pytest.mark.django_db
def test_initiator_can_add_feedback(apiclient, idea, user, comment_factory):
    comment = comment_factory(pk=1, content_object=idea)
    idea.project.organisation.initiators.add(user)

    assert ModeratorCommentFeedback.objects.all().count() == 0
    url = reverse("moderatorfeedback-list", kwargs={"comment_pk": comment.pk})
    data = {"feedback_text": "a statement"}
    apiclient.force_authenticate(user=user)
    response = apiclient.post(url, data)
    assert response.status_code == 201
    assert ModeratorCommentFeedback.objects.all().count() == 1


@pytest.mark.django_db
def test_admin_can_add_feedback(admin, apiclient, idea, comment_factory):
    comment = comment_factory(pk=1, content_object=idea)

    assert ModeratorCommentFeedback.objects.all().count() == 0
    url = reverse("moderatorfeedback-list", kwargs={"comment_pk": comment.pk})
    data = {"feedback_text": "a statement"}
    apiclient.force_authenticate(user=admin)
    response = apiclient.post(url, data)
    assert response.status_code == 201
    assert ModeratorCommentFeedback.objects.all().count() == 1


@pytest.mark.django_db
def test_user_cannot_edit_feedback(
    apiclient, idea, user, comment_factory, moderator_comment_feedback_factory
):
    comment = comment_factory(content_object=idea)
    statement = moderator_comment_feedback_factory(comment=comment)
    assert ModeratorCommentFeedback.objects.all().count() == 1
    url = reverse(
        "moderatorfeedback-detail",
        kwargs={
            "comment_pk": statement.comment.pk,
            "pk": statement.pk,
        },
    )
    data = {"feedback_text": "a changed statement"}
    apiclient.force_authenticate(user=user)
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_can_edit_feedback(
    apiclient, idea, user, comment_factory, moderator_comment_feedback_factory
):
    idea.project.moderators.add(user)
    comment = comment_factory(content_object=idea)
    statement = moderator_comment_feedback_factory(comment=comment)
    assert ModeratorCommentFeedback.objects.all().count() == 1
    url = reverse(
        "moderatorfeedback-detail",
        kwargs={
            "comment_pk": statement.comment.pk,
            "pk": statement.pk,
        },
    )
    data = {"feedback_text": "a changed statement"}
    apiclient.force_authenticate(user=user)
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 200
    assert ModeratorCommentFeedback.objects.all().count() == 1
    assert (
        ModeratorCommentFeedback.objects.first().feedback_text == "a changed statement"
    )


@pytest.mark.django_db
def test_user_cannot_delete_feedback(
    apiclient, idea, user, comment_factory, moderator_comment_feedback_factory
):
    comment = comment_factory(content_object=idea)
    statement = moderator_comment_feedback_factory(comment=comment)
    assert ModeratorCommentFeedback.objects.all().count() == 1
    url = reverse(
        "moderatorfeedback-detail",
        kwargs={
            "comment_pk": statement.comment.pk,
            "pk": statement.pk,
        },
    )
    apiclient.force_authenticate(user=user)
    response = apiclient.delete(url)
    assert response.status_code == 403
    assert ModeratorCommentFeedback.objects.all().count() == 1


@pytest.mark.django_db
def test_moderator_can_delete_feedback(
    apiclient, idea, user, comment_factory, moderator_comment_feedback_factory
):
    idea.project.moderators.add(user)
    comment = comment_factory(content_object=idea)
    statement = moderator_comment_feedback_factory(comment=comment)
    assert ModeratorCommentFeedback.objects.all().count() == 1
    url = reverse(
        "moderatorfeedback-detail",
        kwargs={
            "comment_pk": statement.comment.pk,
            "pk": statement.pk,
        },
    )
    apiclient.force_authenticate(user=user)
    response = apiclient.delete(url)
    assert response.status_code == 204
    assert ModeratorCommentFeedback.objects.all().count() == 0
