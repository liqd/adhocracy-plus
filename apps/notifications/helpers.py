from django.apps import apps
from django.db.models import Q

from .models import NotificationType

# Define notification sections
NOTIFICATION_SECTIONS = {
    "projects": [
        NotificationType.PROJECT_STARTED,
        NotificationType.PROJECT_COMPLETED,
        NotificationType.PROJECT_CREATED,
        NotificationType.PROJECT_DELETED,
        NotificationType.PHASE_STARTED,
        NotificationType.PHASE_ENDED,
        NotificationType.EVENT_ADDED,
        NotificationType.EVENT_SOON,
        NotificationType.EVENT_UPDATE,
        NotificationType.EVENT_CANCELLED,
    ],
    "interactions": [
        NotificationType.PROJECT_MODERATION_INVITATION,
        NotificationType.PROJECT_INVITATION,
        NotificationType.COMMENT_REPLY,
        NotificationType.COMMENT_ON_POST,
        NotificationType.MODERATOR_FEEDBACK,
        NotificationType.MODERATOR_HIGHLIGHT,
        NotificationType.MODERATOR_IDEA_FEEDBACK,
        NotificationType.MODERATOR_BLOCKED_COMMENT,
    ],
}


# Helper function to get notifications by section
def get_notifications_by_section(notifications, section):
    if section not in NOTIFICATION_SECTIONS:
        return notifications.none()

    section_types = NOTIFICATION_SECTIONS[section]
    q_objects = Q()
    for notification_type in section_types:
        q_objects |= Q(notification_type=notification_type)

    return notifications.filter(q_objects)


def _create_notifications(obj, strategy):
    """Helper function to create notifications"""
    Notification = apps.get_model("a4_candy_notifications", "Notification")

    # Get recipients
    in_app_recipients = strategy.get_in_app_recipients(obj)
    email_recipients = strategy.get_email_recipients(obj)

    # Create notifications
    notifications = []
    for recipient in in_app_recipients:
        notification_data = strategy.create_notification_data(obj)
        notifications.append(Notification(recipient=recipient, **notification_data))

    if notifications:
        Notification.objects.bulk_create(notifications)

    # Send emails
    for recipient in email_recipients:
        _send_email_notification(recipient, obj, strategy, notification_data)


def _send_email_notification(recipient, obj, strategy, notification_data):
    """Send email notification"""

    email_class = _map_notification_type_to_email_class(
        notification_data["notification_type"]
    )

    if email_class:
        # Pass object ID instead of object to avoid serialization issues
        email_class.send(recipient, obj.id, notification_data)


def _map_notification_type_to_email_class(notification_type):
    """Map notification type to email class"""
    from . import emails

    email_map = {
        NotificationType.MODERATOR_IDEA_FEEDBACK: emails.NotifyCreatorOnModeratorFeedback,
        NotificationType.MODERATOR_BLOCKED_COMMENT: emails.NotifyCreatorOnModeratorBlocked,
        NotificationType.EVENT_SOON: emails.NotifyFollowersOnUpcomingEventEmail,
        NotificationType.PHASE_STARTED: emails.NotifyFollowersOnPhaseStartedEmail,
        NotificationType.COMMENT_ON_POST: emails.NotifyCreatorEmail,
        NotificationType.PROJECT_CREATED: emails.NotifyInitiatorsOnProjectCreatedEmail,
        NotificationType.PROJECT_DELETED: emails.NotifyInitiatorsOnProjectDeletedEmail,
        # TODO: Add missing mappings:
        # NotificationType.COMMENT_REPLY: emails.???‚,
        # NotificationType.MODERATOR_HIGHLIGHT: emails.???,
        # NotificationType.EVENT_CANCELLED: emails.???,
        # NotificationType.EVENT_ADDED: emails.???,
        # NotificationType.EVENT_UPDATE: emails.???,
        # NotificationType.PROJECT_STARTED: emails.???,
        # NotificationType.PROJECT_COMPLETED: emails.???,
    }
    return email_map.get(notification_type)
