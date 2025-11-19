import pytest
from django.core import mail

from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_notify_creator(idea, comment_factory):
    """Check if creators get emails on comment create."""
    creator = idea.creator
    comment_factory(content_object=idea)

    creator_emails = get_emails_for_address(creator.email)
    assert len(creator_emails) == 1
    assert "commented on your post" in creator_emails[0].subject


# #  TODO: Check what the logic is supposed to be here
@pytest.mark.django_db
def test_notify_creator_exclude_moderator(idea, comment_factory, user):
    """Check if moderators are excluded from creator notifications."""
    creator_moderator = idea.creator
    idea.project.moderators.add(creator_moderator)
    comment_factory(content_object=idea)

    assert len(mail.outbox) == 3
    mails = get_emails_for_address(creator_moderator.email)
    assert len(mails) == 1
    # moderator notification instead of creator notification
    assert "commented on your post" in mails[0].subject


# # TODO: Check
@pytest.mark.django_db
def test_notify_creator_exclude_own_comment(idea, comment_factory):
    """Check if creators does not get email on own comment create."""
    creator = idea.creator
    comment_factory(content_object=idea, creator=creator)

    # 2 emails because of moderator notifications for idea and comment
    assert len(mail.outbox) == 2
