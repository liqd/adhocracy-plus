import pytest


@pytest.mark.django_db
def test_str(idea, comment_factory, moderator_comment_feedback_factory):
    comment = comment_factory(pk=1, content_object=idea)
    feedback = moderator_comment_feedback_factory(
        comment=comment, feedback_text="This is a statement."
    )
    assert str(feedback) == "1 - This is a statement."


@pytest.mark.django_db
def test_project(idea, comment_factory, moderator_comment_feedback_factory):
    comment = comment_factory(content_object=idea)
    feedback = moderator_comment_feedback_factory(
        comment=comment,
    )
    assert feedback.project == comment.project
