from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

from apps.contrib import dates


@pytest.mark.django_db
def test_num_reports(apiclient, report_factory, comment_factory, idea):
    comment_1 = comment_factory(content_object=idea)
    report_factory(content_object=comment_1)

    comment_2 = comment_factory(content_object=idea)
    report_factory(content_object=comment_2)
    report_factory(content_object=comment_2)

    comment_3 = comment_factory(content_object=idea)

    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")
    url = reverse("moderationcomments-list", kwargs={"project_pk": project.pk})
    response = apiclient.get(url)
    assert response.status_code == 200
    assert len(response.data) == 3
    comment_1_data = [
        comment for comment in response.data if comment["pk"] == comment_1.pk
    ][0]
    comment_2_data = [
        comment for comment in response.data if comment["pk"] == comment_2.pk
    ][0]
    comment_3_data = [
        comment for comment in response.data if comment["pk"] == comment_3.pk
    ][0]
    assert comment_1_data["num_reports"] == 1
    assert comment_2_data["num_reports"] == 2
    assert comment_3_data["num_reports"] == 0


@pytest.mark.django_db
def test_last_edit(apiclient, report_factory, comment_factory, idea):
    comment_1 = comment_factory(content_object=idea)
    report_factory(content_object=comment_1)
    comment_2 = comment_factory(content_object=idea)
    report_factory(content_object=comment_2)

    with freeze_time(comment_2.created + timedelta(minutes=3)):
        comment_2.modified = timezone.now()
        comment_2.save()

    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")
    url = reverse("moderationcomments-list", kwargs={"project_pk": project.pk})
    response = apiclient.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2
    comment_1_data = [
        comment for comment in response.data if comment["pk"] == comment_1.pk
    ][0]
    comment_2_data = [
        comment for comment in response.data if comment["pk"] == comment_2.pk
    ][0]

    assert not comment_1_data["is_modified"]
    assert comment_1_data["last_edit"] == dates.get_date_display(comment_1.created)
    assert comment_2_data["is_modified"]
    assert comment_2_data["last_edit"] == dates.get_date_display(comment_2.modified)


@pytest.mark.django_db
def test_fields(
    apiclient, report_factory, comment_factory, idea, moderator_comment_feedback_factory
):
    comment_1 = comment_factory(content_object=idea, is_moderator_marked=True)
    report_factory(content_object=comment_1)

    comment_2 = comment_factory(content_object=idea, is_blocked=True)
    report_factory(content_object=comment_2)
    report_factory(content_object=comment_2)

    comment_3 = comment_factory(content_object=idea, is_removed=True)
    feedback = moderator_comment_feedback_factory(comment=comment_3)

    with freeze_time(comment_2.created + timedelta(minutes=3)):
        comment_2.modified = timezone.now()
        comment_2.save()

    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")
    url = reverse("moderationcomments-list", kwargs={"project_pk": project.pk})
    response = apiclient.get(url)
    assert response.status_code == 200
    assert len(response.data) == 3
    comment_1_data = [
        comment for comment in response.data if comment["pk"] == comment_1.pk
    ][0]
    comment_2_data = [
        comment for comment in response.data if comment["pk"] == comment_2.pk
    ][0]
    comment_3_data = [
        comment for comment in response.data if comment["pk"] == comment_3.pk
    ][0]

    assert comment_1_data["comment"] == comment_1.comment
    assert comment_1_data["comment_url"] == comment_1.get_absolute_url()
    assert comment_1_data["is_unread"]
    assert not comment_1_data["is_blocked"]
    assert comment_1_data["is_moderator_marked"]
    assert not comment_1_data["is_modified"]
    assert comment_1_data["last_edit"] == dates.get_date_display(comment_1.created)
    assert comment_1_data["moderator_feedback"] is None
    assert comment_1_data["num_reports"] == 1
    assert comment_1_data["pk"] == comment_1.pk
    assert comment_1_data["feedback_api_url"] == reverse(
        "moderatorfeedback-list", kwargs={"comment_pk": comment_1.pk}
    )
    assert comment_1_data["user_image"] == comment_1.creator.avatar_fallback
    assert comment_1_data["user_name"] == comment_1.creator.username
    assert comment_1_data["user_profile_url"] == comment_1.creator.get_absolute_url()

    assert comment_2_data["comment"] == comment_2.comment
    assert comment_2_data["comment_url"] == comment_2.get_absolute_url()
    assert comment_2_data["is_unread"]
    assert comment_2_data["is_blocked"]
    assert not comment_2_data["is_moderator_marked"]
    assert comment_2_data["is_modified"]
    assert comment_2_data["last_edit"] == dates.get_date_display(comment_2.modified)
    assert comment_2_data["moderator_feedback"] is None
    assert comment_2_data["num_reports"] == 2
    assert comment_2_data["pk"] == comment_2.pk
    assert comment_2_data["feedback_api_url"] == reverse(
        "moderatorfeedback-list", kwargs={"comment_pk": comment_2.pk}
    )
    assert comment_2_data["user_image"] == comment_2.creator.avatar_fallback
    assert comment_2_data["user_name"] == comment_2.creator.username
    assert comment_2_data["user_profile_url"] == comment_2.creator.get_absolute_url()

    assert comment_3_data["comment"] == comment_3.comment == ""
    assert comment_3_data["comment_url"] == comment_3.get_absolute_url()
    assert comment_3_data["is_unread"]
    assert not comment_3_data["is_blocked"]
    assert not comment_3_data["is_moderator_marked"]
    assert not comment_3_data["is_modified"]
    assert comment_3_data["last_edit"] == dates.get_date_display(comment_3.created)
    assert comment_3_data["moderator_feedback"] is not None
    assert (
        comment_3_data["moderator_feedback"]["feedback_text"] == feedback.feedback_text
    )
    assert comment_3_data["num_reports"] == 0
    assert comment_3_data["pk"] == comment_3.pk
    assert comment_3_data["feedback_api_url"] == reverse(
        "moderatorfeedback-list", kwargs={"comment_pk": comment_3.pk}
    )
    assert comment_3_data["user_image"] is None
    assert comment_3_data["user_name"] == "unknown user"
    assert comment_3_data["user_profile_url"] == ""
