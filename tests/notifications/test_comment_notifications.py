import pytest

from apps.notifications.models import Notification
from apps.notifications.models import NotificationType
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_handle_comment_notifications(
    module_factory, idea_factory, project_factory, comment_factory, user_factory
):
    project = project_factory()
    project.save()

    module = module_factory(project=project)

    idea_author = user_factory()
    idea = idea_factory(module=module, creator=idea_author)

    # Create users
    author = user_factory()
    replier = user_factory()

    # Create a parent comment
    parent_comment = comment_factory(
        content_object=idea, creator=author, project=project
    )

    # Save the comment to trigger the signal
    parent_comment.save()

    # Check that a notification was created for the idea author
    module_comment_notifications = Notification.objects.filter(recipient=idea_author)
    assert module_comment_notifications.count() == 1
    assert (
        module_comment_notifications.first().notification_type
        == NotificationType.COMMENT_ON_POST
    )
    # Check that email notification was sent to the idea author
    idea_author_mails = get_emails_for_address(idea_author.email)
    assert len(idea_author_mails) == 1
    assert idea_author_mails[0].subject.startswith("Reaction to your contribution")

    # Create a reply to the parent comment
    reply_comment = comment_factory(
        content_object=parent_comment, creator=replier, project=project
    )

    # Save the reply to trigger the signal
    reply_comment.save()

    # Check that a notification was created for the parent comment author
    notifications = Notification.objects.filter(recipient=author)
    assert notifications.count() == 1
    assert notifications.first().notification_type == NotificationType.COMMENT_REPLY
    # Check that email notification was sent to the parent comment author
    parent_commenter_mails = get_emails_for_address(author.email)
    assert len(parent_commenter_mails) == 1
    assert parent_commenter_mails[0].subject.startswith("Reaction to your contribution")


@pytest.mark.django_db
def test_idea_author_no_notification_when_commenting_own_idea(
    module_factory, idea_factory, project_factory, comment_factory, user_factory
):
    """Test that idea author does NOT receive notification when commenting on their own idea"""
    project = project_factory()
    project.save()

    module = module_factory(project=project)

    # Create user who is both idea author and commenter
    user = user_factory()
    idea = idea_factory(module=module, creator=user)

    # Create a comment by the same user (idea author commenting on their own idea)
    comment = comment_factory(content_object=idea, creator=user, project=project)

    # Save the comment to trigger the signal
    comment.save()

    # Check that NO notification was created for the idea author
    notifications = Notification.objects.filter(recipient=user)
    assert notifications.count() == 0

    # Check that NO email notification was sent to the idea author
    user_mails = get_emails_for_address(user.email)
    assert len(user_mails) == 0


@pytest.mark.django_db
def test_comment_author_no_notification_when_replying_own_comment(
    module_factory, idea_factory, project_factory, comment_factory, user_factory
):
    """Test that comment author does NOT receive notification when replying to their own comment"""
    project = project_factory()
    project.save()

    module = module_factory(project=project)

    idea_author = user_factory()
    idea = idea_factory(module=module, creator=idea_author)

    # Create a user who will create both parent comment and reply
    user = user_factory()

    # Create a parent comment
    parent_comment = comment_factory(content_object=idea, creator=user, project=project)
    parent_comment.save()

    # Clear any notifications from the parent comment creation
    Notification.objects.all().delete()

    # Create a reply to the parent comment by the SAME user
    reply_comment = comment_factory(
        content_object=parent_comment, creator=user, project=project
    )

    # Save the reply to trigger the signal
    reply_comment.save()

    # Check that NO notification was created for the user (replying to own comment)
    notifications = Notification.objects.filter(recipient=user)
    assert notifications.count() == 0

    # Check that NO email notification was sent to the user
    user_mails = get_emails_for_address(user.email)
    assert len(user_mails) == 0
