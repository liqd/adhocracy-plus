import pytest

from apps.projects import helpers


@pytest.mark.django_db
def test_reported_ideas_are_counted(idea, report_factory):
    project = idea.project

    assert helpers.get_num_reported_unread_comments(project) == 0

    report_factory(content_object=idea)

    assert helpers.get_num_reported_unread_comments(project) == 1


@pytest.mark.django_db
def test_reported_unread_comments_and_ideas_are_counted(
    idea, comment_factory, report_factory
):
    project = idea.project
    reported_comment = comment_factory(content_object=idea)
    report_factory(content_object=reported_comment)
    report_factory(content_object=idea)

    assert helpers.get_num_reported_unread_comments(project) == 2


@pytest.mark.django_db
def test_read_reported_ideas_are_not_counted(idea, report_factory):
    project = idea.project
    report_factory(content_object=idea)
    idea.is_reviewed = True
    idea.save(ignore_modified=True)

    assert helpers.get_num_reported_unread_comments(project) == 0


@pytest.mark.django_db
def test_unread_comments_are_counted(idea, comment_factory):
    project = idea.project
    comment_factory(content_object=idea)
    comment_factory(content_object=idea, is_reviewed=True)

    assert helpers.get_num_unread_comments(project) == 1
