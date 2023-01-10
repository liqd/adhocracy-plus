import pytest
from django.core import mail


@pytest.mark.django_db
def test_notify_moderator_on_create(idea, comment_factory):
    """Check if moderator gets email on idea and comment create."""
    moderator = idea.project.moderators.first()
    comment_factory(content_object=idea)

    # 3 emails because of creator notification for reaction on idea
    assert len(mail.outbox) == 3
    assert mail.outbox[0].to[0] == moderator.email
    assert mail.outbox[0].subject.startswith("An idea was added to the project")
    assert mail.outbox[2].to[0] == moderator.email
    assert mail.outbox[2].subject.startswith("A comment was added to the project")
