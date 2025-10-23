import pytest

from adhocracy4.follows.models import Follow
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
def test_handle_comment_highlighted_notification(
    module_factory, idea_factory, project_factory, comment_factory, user_factory
):
    project = project_factory()
    project.save()

    module = module_factory(project=project)
    idea = idea_factory(module=module)

    # Create comment author
    comment_author = user_factory()

    # Create a comment that is not highlighted initially
    comment = comment_factory(
        content_object=idea,
        creator=comment_author,
        project=project,
        is_moderator_marked=False,
    )

    # Save the comment initially (should not trigger highlight notification)
    comment.save()

    # No notification should be created for initial save
    initial_notifications = Notification.objects.filter(recipient=comment_author)
    assert initial_notifications.count() == 0

    # Update the comment to be highlighted by moderator
    comment.is_moderator_marked = True
    comment.save()

    # Check that a notification was created for the comment author
    highlighted_notifications = Notification.objects.filter(recipient=comment_author)
    assert highlighted_notifications.count() == 1
    assert (
        highlighted_notifications.first().notification_type
        == NotificationType.MODERATOR_HIGHLIGHT
    )


@pytest.mark.django_db
def test_handle_proposal_moderator_feedback_notification(
    moderator_feedback_factory,
    project_factory,
    module_factory,
    proposal_factory,
    user_factory,
):
    project = project_factory()
    module = module_factory(project=project)

    # Create proposal author
    proposal_author = user_factory()

    # Create a proposal with initial moderator status
    proposal = proposal_factory(
        module=module,
        creator=proposal_author,
    )

    # Save the proposal initially (should not trigger notification)
    proposal.save()

    # No notification should be created for initial save
    initial_notifications = Notification.objects.filter(recipient=proposal_author)
    assert initial_notifications.count() == 0

    # Update the proposal with moderator feedback
    proposal.moderator_status = "approved"
    proposal.moderator_feedback_text = moderator_feedback_factory(
        feedback_text="Great proposal!"
    )
    proposal.save()

    # Check that a notification was created for the proposal author
    feedback_notifications = Notification.objects.filter(recipient=proposal_author)
    assert feedback_notifications.count() == 1
    assert (
        feedback_notifications.first().notification_type
        == NotificationType.MODERATOR_IDEA_FEEDBACK
    )


@pytest.mark.django_db
def test_handle_idea_moderator_feedback_notification(
    moderator_feedback_factory,
    project_factory,
    module_factory,
    idea_factory,
    user_factory,
):
    project = project_factory()
    module = module_factory(project=project)

    # Create idea author
    idea_author = user_factory()

    # Create an idea with initial moderator status
    idea = idea_factory(
        module=module,
        creator=idea_author,
    )

    # Save the idea initially (should not trigger notification)
    idea.save()

    # No notification should be created for initial save
    initial_notifications = Notification.objects.filter(recipient=idea_author)
    assert initial_notifications.count() == 0

    # Update the idea with moderator feedback
    idea.moderator_status = "approved"
    idea.moderator_feedback_text = moderator_feedback_factory(
        feedback_text="Great idea!"
    )
    idea.save()

    # Check that a notification was created for the idea author
    feedback_notifications = Notification.objects.filter(recipient=idea_author)
    assert feedback_notifications.count() == 1
    assert (
        feedback_notifications.first().notification_type
        == NotificationType.MODERATOR_IDEA_FEEDBACK
    )


@pytest.mark.django_db
def test_handle_comment_blocked_notification(
    module_factory, idea_factory, project_factory, comment_factory, user_factory
):
    project = project_factory()
    module = module_factory(project=project)
    idea = idea_factory(module=module)

    # Create comment author
    comment_author = user_factory()

    # Create a comment that is not blocked initially
    comment = comment_factory(
        content_object=idea, creator=comment_author, project=project, is_blocked=False
    )

    # Save the comment initially (should not trigger notification)
    comment.save()

    # No notification should be created for initial save
    initial_notifications = Notification.objects.filter(recipient=comment_author)
    assert initial_notifications.count() == 0

    # Update the comment to be blocked by moderator
    comment.is_blocked = True
    comment.save()

    # Check that a notification was created for the comment author
    blocked_notifications = Notification.objects.filter(recipient=comment_author)
    assert blocked_notifications.count() == 1
    assert (
        blocked_notifications.first().notification_type
        == NotificationType.MODERATOR_BLOCKED_COMMENT
    )


@pytest.mark.django_db
def test_handle_offline_event_deleted_notification(
    project_factory, offline_event_factory, user_factory
):
    project = project_factory()

    # Create event attendees/followers
    attendee = user_factory()

    # Create an offline event
    offline_event = offline_event_factory(project=project)

    # Make user a follower of the project
    Follow.objects.get_or_create(
        project=project,
        creator=attendee,
        defaults={"enabled": True},
    )

    # Delete the event to trigger the signal
    offline_event.delete()

    # Check that a notification was created for the attendee
    deleted_notifications = Notification.objects.filter(recipient=attendee)
    assert deleted_notifications.count() == 1
    assert (
        deleted_notifications.first().notification_type
        == NotificationType.EVENT_CANCELLED
    )


@pytest.mark.django_db
def test_handle_offline_event_created_notification(
    project_factory, offline_event_factory, user_factory
):
    project = project_factory()

    # Create event attendees/followers
    attendee = user_factory()

    # Make user a follower of the project
    Follow.objects.get_or_create(
        project=project,
        creator=attendee,
        defaults={"enabled": True},
    )

    # Create an offline event
    offline_event = offline_event_factory(project=project)

    # Check that a notification was created for the attendee
    created_notifications = Notification.objects.filter(recipient=attendee)
    assert created_notifications.count() == 1
    assert (
        created_notifications.first().notification_type == NotificationType.EVENT_ADDED
    )


@pytest.mark.django_db
def test_handle_event_update_notifications(
    project_factory, offline_event_factory, user_factory
):
    project = project_factory()

    # Create event attendees/followers
    attendee = user_factory()

    # Create an offline event with initial date
    offline_event = offline_event_factory(project=project, date="2024-01-01 12:00:00")

    # Make user a follower of the project
    Follow.objects.get_or_create(
        project=project,
        creator=attendee,
        defaults={"enabled": True},
    )

    offline_event.save()

    # Update the event date to trigger the signal
    offline_event.date = "2024-01-02 14:00:00"
    offline_event.save()

    # Check that a notification was created for the attendee
    updated_notifications = Notification.objects.filter(recipient=attendee)
    assert updated_notifications.count() == 2
    assert (
        updated_notifications.last().notification_type == NotificationType.EVENT_UPDATE
    )

@pytest.mark.django_db
def test_handle_invite_notification(
    project_factory, participant_invite_factory, user_factory
):
    project = project_factory()

    # Create a user who will receive the invitation
    invited_user = user_factory()

    # Create a project invitation for the user
    moderator_invite = participant_invite_factory(
        project=project, email=invited_user.email
    )

    # Check that a notification was created for the invited user
    invitation_notifications = Notification.objects.filter(recipient=invited_user)
    assert invitation_notifications.count() == 1
    assert (
        invitation_notifications.first().notification_type
        == NotificationType.PROJECT_INVITATION
    )


@pytest.mark.django_db
def test_handle_moderator_invite_notification(
    project_factory, moderator_invite_factory, user_factory
):
    project = project_factory()

    # Create a user who will receive the invitation
    invited_user = user_factory()

    # Create a moderator invitation for the user
    moderator_invite = moderator_invite_factory(
        project=project, email=invited_user.email
    )

    # Check that a notification was created for the invited user
    invitation_notifications = Notification.objects.filter(recipient=invited_user)
    assert invitation_notifications.count() == 1
    assert (
        invitation_notifications.first().notification_type
        == NotificationType.PROJECT_MODERATION_INVITATION
    )

@pytest.mark.django_db
def test_handle_project_created(
    project_factory, organisation_factory, user_factory
):
    initiator = user_factory()

    # Create organisation with this initiator
    organisation = organisation_factory()
    organisation.initiators.add(initiator)

    project = project_factory(organisation=organisation)

    # Check that a notification was created for the initiator
    creation_notifications = Notification.objects.filter(recipient=initiator)
    assert creation_notifications.count() == 1
    assert (
        creation_notifications.first().notification_type
        == NotificationType.PROJECT_CREATED
    )

@pytest.mark.django_db
def test_handle_project_deleted(project_factory, organisation_factory, user_factory):
    initiator = user_factory()

    # Create organisation with this initiator
    organisation = organisation_factory()
    organisation.initiators.add(initiator)

    # Create project in this organisation
    project = project_factory(organisation=organisation)

    # Delete the project to trigger the signal
    project.delete()

    # Check that a notification was created for the initiator
    deletion_notifications = Notification.objects.filter(recipient=initiator)
    assert deletion_notifications.count() == 2
    assert (
        deletion_notifications.first().notification_type
        == NotificationType.PROJECT_DELETED
    )

@pytest.mark.django_db
def test_handle_idea_created(
    project_factory, module_factory, user_factory, idea_factory
):
    project = project_factory()

    module = module_factory(project=project)

    idea_author = user_factory()
    idea = idea_factory(module=module, creator=idea_author)
    moderator = idea.project.moderators.first()
    # Check that a notification was created for the moderator
    invitation_notifications = Notification.objects.filter(recipient=moderator)
    assert invitation_notifications.count() == 1
    assert (
        invitation_notifications.first().notification_type
        == NotificationType.USER_CONTENT_CREATED
    )


@pytest.mark.django_db
def test_handle_proposal_created(
    project_factory, module_factory, user_factory, proposal_factory
):
    project = project_factory()
    module = module_factory(project=project)
    
    proposal_author = user_factory()
    proposal = proposal_factory(module=module, creator=proposal_author)
    moderator = proposal.project.moderators.first()
    
    # Check that a notification was created for the moderator
    notifications = Notification.objects.filter(recipient=moderator)
    assert notifications.count() == 1
    assert (
        notifications.first().notification_type
        == NotificationType.USER_CONTENT_CREATED
    )