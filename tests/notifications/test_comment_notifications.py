import pytest

from apps.notifications.models import Notification
from apps.notifications.models import NotificationType
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_handle_comment_notifications(
    module_factory, idea_factory, project_factory, comment_factory, user_factory
):
    # Setup
    project = project_factory()
    module = module_factory(project=project)
    idea_author = user_factory()
    idea = idea_factory(module=module, creator=idea_author)
    author = user_factory()
    replier = user_factory()

    # Test comment on idea
    parent_comment = comment_factory(
        content_object=idea, creator=author, project=project
    )

    # Assert comment notification
    idea_author_notifications = Notification.objects.filter(recipient=idea_author)
    assert idea_author_notifications.count() == 1
    notification = idea_author_notifications.first()
    assert notification.notification_type == NotificationType.COMMENT_ON_POST

    # Assert email
    idea_author_emails = get_emails_for_address(idea_author.email)
    assert len(idea_author_emails) == 1
    assert author.username in idea_author_emails[0].subject
    assert idea.name in idea_author_emails[0].subject
    assert "commented on your post" in idea_author_emails[0].subject

    # Test reply to comment
    comment_factory(content_object=parent_comment, creator=replier, project=project)

    # Assert reply notification
    author_notifications = Notification.objects.filter(recipient=author)
    assert author_notifications.count() == 1
    assert (
        author_notifications.first().notification_type == NotificationType.COMMENT_REPLY
    )

    # Assert email
    author_emails = get_emails_for_address(author.email)
    assert len(author_emails) == 1
    assert replier.username in author_emails[0].subject
    assert "replied to your comment" in author_emails[0].subject


@pytest.mark.django_db
def test_idea_author_no_notification_when_commenting_own_idea(
    module_factory, idea_factory, project_factory, comment_factory, user_factory
):
    # Setup - user is both idea author and commenter
    project = project_factory()
    module = module_factory(project=project)
    user = user_factory()
    idea = idea_factory(module=module, creator=user)

    Notification.objects.all().delete()
    # Action - comment on own idea
    comment_factory(content_object=idea, creator=user, project=project)
    # Assert no notifications
    assert Notification.objects.count() == 0
    assert len(get_emails_for_address(user.email)) == 0


@pytest.mark.django_db
def test_comment_author_no_notification_when_replying_own_comment(
    module_factory, idea_factory, project_factory, comment_factory, user_factory
):
    # Setup
    project = project_factory()
    module = module_factory(project=project)
    idea_author = user_factory()
    idea = idea_factory(module=module, creator=idea_author)
    user = user_factory()

    # Create parent comment
    parent_comment = comment_factory(content_object=idea, creator=user, project=project)

    # Clear previous notifications
    Notification.objects.all().delete()

    # Action - reply to own comment
    comment_factory(content_object=parent_comment, creator=user, project=project)

    # Assert no notifications
    assert Notification.objects.count() == 0
    assert len(get_emails_for_address(user.email)) == 0
