import pytest
from django.core import mail
from django.urls import reverse

from adhocracy4.test.helpers import redirect_target
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_notify_creator(idea, comment_factory):
    """Check if creators get emails on comment create."""
    creator = idea.creator
    comment = comment_factory(content_object=idea)

    creator_emails = get_emails_for_address(creator.email)
    assert len(creator_emails) == 1
    assert creator_emails[0].subject.startswith("Reaction to your contribution")

    comment_creator = comment.creator
    comment_factory(content_object=comment)

    # 2 more emails because of moderator notification
    comment_creator_emails = get_emails_for_address(comment_creator.email)
    assert len(comment_creator_emails) == 1
    assert comment_creator_emails[0].subject.startswith("Reaction to your contribution")


#  TODO: Check what the logic is supposed to be here
# @pytest.mark.django_db
# def test_notify_creator_exclude_moderator(idea, comment_factory, user):
#     """Check if moderators are excluded from creator notifications."""
#     creator_moderator = idea.creator
#     idea.project.moderators.add(creator_moderator)
#     comment_factory(content_object=idea)

#     assert len(mail.outbox) == 3
#     mails = get_emails_for_address(creator_moderator.email)
#     assert len(mails) == 1
#     # moderator notification instead of creator notification
#     assert not mails[0].subject.startswith("Reaction to your contribution")
#     assert mails[0].subject.startswith("A comment was added to the project")


# TODO: Check
@pytest.mark.django_db
def test_notify_creator_exclude_own_comment(idea, comment_factory):
    """Check if creators does not get email on own comment create."""
    creator = idea.creator
    comment_factory(content_object=idea, creator=creator)

    # 2 emails because of moderator notifications for idea and comment
    assert len(mail.outbox) == 2


# TODO: Check
@pytest.mark.django_db
def test_notify_creator_on_moderator_feedback(proposal_factory, client):
    """Check if creator gets emails on moderator feedback."""
    proposal = proposal_factory()
    # moderator notifications for proposal
    assert len(mail.outbox) == 1

    creator = proposal.creator
    project = proposal.project
    moderator = project.moderators.first()

    url = reverse(
        "a4_candy_budgeting:proposal-moderate",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "pk": proposal.pk,
            "year": proposal.created.year,
        },
    )
    client.login(username=moderator.email, password="password")

    data = {
        "moderator_status": "test",
        "is_archived": False,
        "feedback_text": "its a feedback text",
    }
    response = client.post(url, data)
    assert redirect_target(response) == "proposal-detail"

    # 2nd email about moderator feedback
    creator_emails = get_emails_for_address(creator.email)
    assert len(creator_emails) == 1
    assert creator_emails[0].subject.startswith("Feedback for your contribution")
