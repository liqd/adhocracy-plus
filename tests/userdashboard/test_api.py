from datetime import timedelta

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_anonymous_cannot_view_moderation_comments(apiclient, project):
    url = reverse("moderationcomments-list", kwargs={"project_pk": project.pk})
    response = apiclient.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_wrong_moderator_cannot_view_moderation_comments(apiclient, project_factory):
    project_1 = project_factory()
    project_2 = project_factory()

    moderator = project_1.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    url = reverse("moderationcomments-list", kwargs={"project_pk": project_2.pk})
    response = apiclient.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_can_view_moderation_comments(apiclient, comment_factory, idea):
    comment_1 = comment_factory(content_object=idea)
    comment_2 = comment_factory(content_object=idea)
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    url = reverse("moderationcomments-list", kwargs={"project_pk": project.pk})
    response = apiclient.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2
    assert comment_1.pk in response.data[1].values()
    assert comment_2.pk in response.data[0].values()


@pytest.mark.django_db
def test_moderator_can_block_and_highlight_comment(apiclient, comment_factory, idea):
    comment_1 = comment_factory(content_object=idea)
    comment_2 = comment_factory(content_object=idea)
    project = idea.project
    moderator = project.moderators.first()
    assert not comment_1.is_blocked
    assert not comment_2.is_moderator_marked

    apiclient.login(username=moderator.email, password="password")

    url_comment_1 = reverse(
        "moderationcomments-detail",
        kwargs={"project_pk": project.pk, "pk": comment_1.pk},
    )
    data = {"is_blocked": True}
    response = apiclient.patch(url_comment_1, data, format="json")
    assert response.status_code == 200

    url_comment_2 = reverse(
        "moderationcomments-detail",
        kwargs={"project_pk": project.pk, "pk": comment_2.pk},
    )
    data = {"is_moderator_marked": True}
    response = apiclient.patch(url_comment_2, data, format="json")
    assert response.status_code == 200

    comment_1.refresh_from_db()
    comment_2.refresh_from_db()
    assert comment_1.is_blocked
    assert comment_2.is_moderator_marked


@pytest.mark.django_db
def test_moderator_can_mark_comment_read(apiclient, comment_factory, idea):
    comment = comment_factory(content_object=idea)
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    url = reverse(
        "moderationcomments-detail", kwargs={"project_pk": project.pk, "pk": comment.pk}
    )
    filter_string = "?is_reviewed=all"
    response = apiclient.get(url + filter_string)
    assert response.status_code == 200
    assert not comment.is_reviewed
    assert response.data["is_unread"]

    url_archive = url + "mark_read/"
    response = apiclient.get(url_archive + filter_string)
    assert response.status_code == 200
    comment.refresh_from_db()
    assert comment.is_reviewed
    assert not response.data["is_unread"]

    url_unarchive = url + "mark_unread/"
    response = apiclient.get(url_unarchive + filter_string)
    assert response.status_code == 200
    comment.refresh_from_db()
    assert not comment.is_reviewed
    assert response.data["is_unread"]


@pytest.mark.django_db
def test_queryset_and_filters(apiclient, report_factory, comment_factory, idea_factory):
    idea = idea_factory(module__project__pk=1)
    other_idea = idea_factory(module__project__pk=2)
    project = idea.project

    delay = timedelta(hours=2)
    comment_1 = comment_factory(content_object=idea)
    comment_2 = comment_factory(
        content_object=idea, created=comment_1.created - delay, is_reviewed=True
    )
    comment_3 = comment_factory(content_object=idea, created=comment_1.created + delay)
    comment_4 = comment_factory(
        content_object=idea, created=comment_1.created + 2 * delay, is_reviewed=True
    )
    comment_5 = comment_factory(content_object=other_idea)

    # comment_1 with 2 reports
    report_factory(content_object=comment_1)
    report_factory(content_object=comment_1)
    # comment_2 with 1 report, is read
    report_factory(content_object=comment_2)
    # comment_3 with 1 report
    report_factory(content_object=comment_3)
    # comment_4 with no reports, is read
    # comment_5 in other project with 1 report
    report_factory(content_object=comment_5)

    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    url = reverse("moderationcomments-list", kwargs={"project_pk": project.pk})

    # test default filters
    response = apiclient.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2
    comment_pks = [comment["pk"] for comment in response.data]
    assert comment_pks == [comment_1.pk, comment_3.pk]

    # test default sorting is most reported (second sorting -created)
    filter_string = "?is_reviewed=all"
    response = apiclient.get(url + filter_string)
    assert response.status_code == 200
    assert len(response.data) == 4
    comment_pks = [comment["pk"] for comment in response.data]
    assert comment_pks == [comment_1.pk, comment_3.pk, comment_2.pk, comment_4.pk]

    filter_string = "?is_reviewed=all&has_reports=False"
    response = apiclient.get(url + filter_string)
    assert response.status_code == 200
    assert len(response.data) == 1
    comment_pks = [comment["pk"] for comment in response.data]
    assert comment_pks == [comment_4.pk]

    filter_string = "?has_reports=False"
    response = apiclient.get(url + filter_string)
    assert response.status_code == 200
    assert len(response.data) == 0

    filter_string = "?is_reviewed=all&ordering=created"
    response = apiclient.get(url + filter_string)
    assert response.status_code == 200
    assert len(response.data) == 4
    comment_pks = [comment["pk"] for comment in response.data]
    assert comment_pks == [comment_2.pk, comment_1.pk, comment_3.pk, comment_4.pk]


@pytest.mark.django_db
def test_comment_not_modified_when_blocked(apiclient, comment_factory, idea):
    comment = comment_factory(content_object=idea)
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    assert not comment.is_blocked
    assert not comment.modified

    url = reverse(
        "moderationcomments-detail", kwargs={"project_pk": project.pk, "pk": comment.pk}
    )

    data = {"is_blocked": True}

    response = apiclient.patch(url, data)
    assert response.status_code == 200
    comment.refresh_from_db()
    assert comment.is_blocked
    assert not comment.modified


@pytest.mark.django_db
def test_comment_not_modified_when_moderator_marked(apiclient, comment_factory, idea):
    comment = comment_factory(content_object=idea)
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    assert not comment.is_moderator_marked
    assert not comment.modified

    url = reverse(
        "moderationcomments-detail", kwargs={"project_pk": project.pk, "pk": comment.pk}
    )
    data = {"is_moderator_marked": True}

    response = apiclient.patch(url, data)
    assert response.status_code == 200
    comment.refresh_from_db()
    assert comment.is_moderator_marked
    assert not comment.modified


@pytest.mark.django_db
def test_comment_not_modified_when_marked_read_or_unread(
    apiclient, comment_factory, idea
):
    comment = comment_factory(content_object=idea)
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password="password")

    assert not comment.is_reviewed
    assert not comment.modified

    url = reverse(
        "moderationcomments-detail", kwargs={"project_pk": project.pk, "pk": comment.pk}
    )
    response = apiclient.get(url + "mark_read/")
    assert response.status_code == 200
    comment.refresh_from_db()
    assert comment.is_reviewed
    assert not comment.modified

    # need the filter string as default filter only returns non reviewed comments
    response = apiclient.get(url + "mark_unread/?is_reviewed=all")
    assert response.status_code == 200
    comment.refresh_from_db()
    assert not comment.is_reviewed
    assert not comment.modified
