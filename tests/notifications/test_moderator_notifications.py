import pytest

from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_notify_moderator_on_create(idea, comment_factory):
    """Check if moderator gets email on idea and comment create."""
    moderator = idea.project.moderators.first()
    comment_factory(content_object=idea)

    moderator_emails = get_emails_for_address(moderator.email)
    assert len(moderator_emails) == 1
    assert moderator_emails[0].subject.startswith("An Idea was added to the project")
