import pytest
from django.urls import reverse
from rest_framework import status

from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import setup_phase
from adhocracy4.test.helpers import setup_users
from apps.ideas.phases import CollectPhase
from apps.ideas.phases import RatingPhase


@pytest.mark.django_db
def test_authenticated_user_can_edit_own_comment(
    comment_factory,
    apiclient,
    phase_factory,
    idea_factory,
    organisation_terms_of_use_factory,
):
    phase, _, _, idea = setup_phase(phase_factory, idea_factory, CollectPhase)
    comment = comment_factory(content_object=idea)
    organisation_terms_of_use_factory(
        user=comment.creator,
        organisation=comment.project.organisation,
        has_agreed=True,
    )

    apiclient.force_authenticate(user=comment.creator)
    url = reverse(
        "comments-detail",
        kwargs={
            "pk": comment.pk,
            "content_type": comment.content_type.pk,
            "object_pk": comment.object_pk,
        },
    )
    data = {"comment": "comment comment comment"}
    with freeze_phase(phase):
        response = apiclient.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["comment"] == "comment comment comment"


@pytest.mark.django_db
def test_user_can_not_edit_comment_of_other_user(
    apiclient,
    user2,
    comment_factory,
    idea_factory,
    phase_factory,
    organisation_terms_of_use_factory,
):
    phase, _, _, idea = setup_phase(phase_factory, idea_factory, CollectPhase)
    comment = comment_factory(content_object=idea)
    organisation_terms_of_use_factory(
        user=comment.creator,
        organisation=comment.project.organisation,
        has_agreed=True,
    )
    organisation_terms_of_use_factory(
        user=user2,
        organisation=comment.project.organisation,
        has_agreed=True,
    )
    apiclient.force_authenticate(user=user2)
    url = reverse(
        "comments-detail",
        kwargs={
            "pk": comment.pk,
            "content_type": comment.content_type.pk,
            "object_pk": comment.object_pk,
        },
    )
    data = {"comment": "comment comment comment"}

    with freeze_phase(phase):
        response = apiclient.patch(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_anonymous_user_can_not_edit_comment(
    apiclient,
    comment_factory,
    idea_factory,
    phase_factory,
    organisation_terms_of_use_factory,
):
    phase, _, _, idea = setup_phase(phase_factory, idea_factory, CollectPhase)
    comment = comment_factory(content_object=idea)
    organisation_terms_of_use_factory(
        user=comment.creator,
        organisation=comment.project.organisation,
        has_agreed=True,
    )
    apiclient.force_authenticate(user=None)
    url = reverse(
        "comments-detail",
        kwargs={
            "pk": comment.pk,
            "content_type": comment.content_type.pk,
            "object_pk": comment.object_pk,
        },
    )
    data = {"comment": "comment comment comment"}

    with freeze_phase(phase):
        response = apiclient.patch(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_of_comment_can_edit_comment(
    admin, apiclient, comment_factory, idea, organisation_terms_of_use_factory
):
    comment = comment_factory(content_object=idea)
    organisation_terms_of_use_factory(
        user=admin,
        organisation=comment.project.organisation,
        has_agreed=True,
    )
    url = reverse(
        "comments-detail",
        kwargs={
            "pk": comment.pk,
            "content_type": comment.content_type.pk,
            "object_pk": comment.object_pk,
        },
    )
    data = {"comment": "comment comment comment"}
    apiclient.force_authenticate(user=admin)
    response = apiclient.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["comment"] == "comment comment comment"


@pytest.mark.django_db
def test_moderator_cannot_edit_comment(
    apiclient,
    comment_factory,
    idea_factory,
    phase_factory,
    organisation_terms_of_use_factory,
):

    phase, _, project, idea = setup_phase(phase_factory, idea_factory, CollectPhase)

    _, moderator, _ = setup_users(project)

    comment = comment_factory(content_object=idea)
    organisation_terms_of_use_factory(
        user=moderator,
        organisation=comment.project.organisation,
        has_agreed=True,
    )

    apiclient.force_authenticate(user=moderator)
    url = reverse(
        "comments-detail",
        kwargs={
            "pk": comment.pk,
            "content_type": comment.content_type.pk,
            "object_pk": comment.object_pk,
        },
    )
    data = {"comment": "comment comment comment"}

    with freeze_phase(phase):
        response = apiclient.patch(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_initiator_cannot_edit_comment(
    apiclient,
    comment_factory,
    idea_factory,
    phase_factory,
    organisation_terms_of_use_factory,
):

    phase, _, project, idea = setup_phase(phase_factory, idea_factory, CollectPhase)

    _, _, initiator = setup_users(project)

    comment = comment_factory(content_object=idea)
    organisation_terms_of_use_factory(
        user=initiator,
        organisation=comment.project.organisation,
        has_agreed=True,
    )

    apiclient.force_authenticate(user=initiator)
    url = reverse(
        "comments-detail",
        kwargs={
            "pk": comment.pk,
            "content_type": comment.content_type.pk,
            "object_pk": comment.object_pk,
        },
    )
    data = {"comment": "comment comment comment"}

    with freeze_phase(phase):
        response = apiclient.patch(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_creater_of_comment_can_set_removed_flag(
    apiclient, comment_factory, idea_factory, phase_factory
):
    phase, _, project, idea = setup_phase(phase_factory, idea_factory, CollectPhase)

    comment = comment_factory(content_object=idea)
    url = reverse(
        "comments-detail",
        kwargs={
            "pk": comment.pk,
            "content_type": comment.content_type.pk,
            "object_pk": comment.object_pk,
        },
    )
    apiclient.force_authenticate(user=comment.creator)

    with freeze_phase(phase):
        response = apiclient.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["is_deleted"] is True
    assert response.data["comment"] == ""


@pytest.mark.django_db
def test_moderator_of_comment_can_set_censored_flag(
    apiclient, comment_factory, idea_factory, phase_factory
):

    phase, _, project, idea = setup_phase(phase_factory, idea_factory, RatingPhase)
    _, moderator, _ = setup_users(project)
    comment = comment_factory(content_object=idea)

    url = reverse(
        "comments-detail",
        kwargs={
            "pk": comment.pk,
            "content_type": comment.content_type.pk,
            "object_pk": comment.object_pk,
        },
    )
    apiclient.force_authenticate(user=moderator)
    response = apiclient.delete(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["is_deleted"] is True
    assert response.data["comment"] == ""
