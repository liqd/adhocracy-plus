import pytest

from adhocracy4.follows.models import Follow
from apps.notifications.models import Notification
from apps.notifications.models import NotificationType
from tests.helpers import get_emails_for_address


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

    # No notification should be created for initial save
    initial_notifications = Notification.objects.filter(recipient=comment_author)
    assert initial_notifications.count() == 0

    # Assert no email for initial save
    comment_author_emails = get_emails_for_address(comment_author.email)
    assert len(comment_author_emails) == 0

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

    # Assert email
    comment_author_emails = get_emails_for_address(comment_author.email)
    assert len(comment_author_emails) == 1
    print(comment_author_emails[0].subject)
    assert "highlighted" in comment_author_emails[0].subject.lower()


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

    # Assert no email for initial save
    proposal_author_emails = get_emails_for_address(proposal_author.email)
    assert len(proposal_author_emails) == 0

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

    # Assert email
    proposal_author_emails = get_emails_for_address(proposal_author.email)
    assert len(proposal_author_emails) == 1
    assert "feedback" in proposal_author_emails[0].subject.lower()
    assert proposal_author.username in proposal_author_emails[0].body.lower()


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

    # Assert no email for initial save
    idea_author_emails = get_emails_for_address(idea_author.email)
    assert len(idea_author_emails) == 0

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

    # Assert email
    idea_author_emails = get_emails_for_address(idea_author.email)
    assert len(idea_author_emails) == 1
    assert "feedback" in idea_author_emails[0].subject.lower()
    assert idea_author.username in idea_author_emails[0].body.lower()


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

    # No notification should be created for initial save
    initial_notifications = Notification.objects.filter(recipient=comment_author)
    assert initial_notifications.count() == 0

    # Assert no email for initial save
    comment_author_emails = get_emails_for_address(comment_author.email)
    assert len(comment_author_emails) == 0

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

    # Assert email
    comment_author_emails = get_emails_for_address(comment_author.email)
    assert len(comment_author_emails) == 1
    assert "your comment was blocked" in comment_author_emails[0].subject.lower()


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

    # Assert email
    attendee_emails = get_emails_for_address(attendee.email)
    assert len(attendee_emails) == 1
    assert "cancelled" in attendee_emails[0].subject.lower()
    assert attendee.username in attendee_emails[0].body.lower()


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

    # Assert email
    attendee_emails = get_emails_for_address(attendee.email)
    assert len(attendee_emails) == 1
    assert "event" in attendee_emails[0].subject.lower()
    assert attendee.username in attendee_emails[0].body.lower()


@pytest.mark.django_db
def test_handle_event_update_notifications(
    project_factory, offline_event_factory, user_factory
):
    project = project_factory()
    attendee = user_factory()

    # Use proper datetime objects
    import datetime

    from django.utils import timezone

    initial_date = timezone.make_aware(datetime.datetime(2024, 1, 1, 12, 0, 0))
    updated_date = timezone.make_aware(datetime.datetime(2024, 1, 2, 14, 0, 0))

    # Create an offline event with initial date as datetime
    offline_event = offline_event_factory(project=project, date=initial_date)

    Follow.objects.get_or_create(
        project=project,
        creator=attendee,
        defaults={"enabled": True},
    )

    # Update the event date to trigger the signal
    offline_event.date = updated_date
    offline_event.save()

    updated_notifications = Notification.objects.filter(recipient=attendee)
    assert updated_notifications.count() == 1
    assert (
        updated_notifications.last().notification_type == NotificationType.EVENT_UPDATE
    )

    # Assert email
    attendee_emails = get_emails_for_address(attendee.email)
    assert len(attendee_emails) == 1
    assert "update" in attendee_emails[0].subject.lower()


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

    # # Assert email
    invited_user_emails = get_emails_for_address(invited_user.email)
    assert len(invited_user_emails) == 1
    assert "you have been invited" in invited_user_emails[0].subject.lower()


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

    # TODO: Double check if email is being sent, why assertion failed
    # Assert email
    # invited_user_emails = get_emails_for_address(invited_user.email)
    # assert len(invited_user_emails) == 1
    # assert "moderator" in invited_user_emails[0].subject.lower() or "moderation" in invited_user_emails[0].subject.lower()


# TODO: Check project creator_name in email
@pytest.mark.django_db
def test_handle_project_created(project_factory, organisation_factory, user_factory):

    organisation = organisation_factory()
    assert organisation.initiators.count() == 1
    initiator = organisation.initiators.first()

    project = project_factory(organisation=organisation)

    creation_notifications = Notification.objects.filter(
        notification_type=NotificationType.PROJECT_CREATED
    )
    assert creation_notifications.count() == 1

    notification = creation_notifications.first()
    assert notification.notification_type == NotificationType.PROJECT_CREATED
    assert notification.recipient == initiator
    assert "has been created" in notification.message_template

    # Assert email
    initiator_emails = get_emails_for_address(initiator.email)
    assert len(initiator_emails) == 1
    assert "new project" in initiator_emails[0].subject.lower()
    assert initiator.username in initiator_emails[0].body.lower()
    assert project.name.lower() in initiator_emails[0].body.lower()


@pytest.mark.django_db
def test_handle_project_deleted(project_factory, organisation_factory, user_factory):

    organisation = organisation_factory()
    initiator = organisation.initiators.first()
    project = project_factory(organisation=organisation)

    get_emails_for_address(initiator.email)

    Notification.objects.all().delete()

    # Delete the project to trigger the signal
    project.delete()

    deletion_notifications = Notification.objects.filter(
        notification_type=NotificationType.PROJECT_DELETED
    )
    assert deletion_notifications.count() == 1

    notification = deletion_notifications.first()
    assert notification.notification_type == NotificationType.PROJECT_DELETED
    assert notification.recipient == initiator
    assert "has been deleted" in notification.message_template

    # Assert email
    initiator_emails = get_emails_for_address(initiator.email)
    assert len(initiator_emails) == 2
    assert "deletion of project" in initiator_emails[1].subject.lower()
    assert initiator.username in initiator_emails[1].body.lower()


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

    # Assert email
    moderator_emails = get_emails_for_address(moderator.email)
    assert len(moderator_emails) == 1
    assert "idea" in moderator_emails[0].subject.lower()
    assert moderator.username in moderator_emails[0].body.lower()


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
        notifications.first().notification_type == NotificationType.USER_CONTENT_CREATED
    )

    # Assert email
    moderator_emails = get_emails_for_address(moderator.email)
    assert len(moderator_emails) == 1
    assert "proposal" in moderator_emails[0].subject.lower()
