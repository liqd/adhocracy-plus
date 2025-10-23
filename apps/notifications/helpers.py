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
        NotificationType.USER_CONTENT_CREATED,
    ],
    "interactions": [
        NotificationType.PROJECT_MODERATION_INVITATION,
        NotificationType.PROJECT_INVITATION,
        NotificationType.COMMENT_REPLY,
        NotificationType.COMMENT_ON_POST,
        NotificationType.MODERATOR_COMMENT_FEEDBACK,
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

    # Send emails - ALL at once
    if email_recipients:
        print(
            f"Sending emails to {len(email_recipients)} recipients for {notification_data['notification_type']}"
        )
        _send_email_notifications(email_recipients, obj, strategy, notification_data)


def _send_email_notifications(recipients, obj, strategy, notification_data):

    email_class = _map_notification_type_to_email_class(
        notification_data["notification_type"]
    )

    if email_class:
        recipient_ids = [
            recipient.id if hasattr(recipient, "id") else recipient
            for recipient in recipients
        ]

        # Pass the recipient_ids as kwargs to the send method
        email_class.send(
            obj,
            strategy_recipient_ids=recipient_ids,
            notification_data=notification_data,
        )


def _map_notification_type_to_email_class(notification_type):
    """Map notification type to email class"""
    from . import emails

    email_map = {
        NotificationType.MODERATOR_COMMENT_FEEDBACK: emails.NotifyCreatorOnModeratorFeedback,
        NotificationType.MODERATOR_IDEA_FEEDBACK: emails.NotifyCreatorOnModeratorFeedback,
        NotificationType.MODERATOR_BLOCKED_COMMENT: emails.NotifyCreatorOnModeratorBlocked,
        NotificationType.EVENT_SOON: emails.NotifyFollowersOnUpcomingEventEmail,
        NotificationType.PROJECT_STARTED: emails.NotifyFollowersOnProjectStartedEmail,
        NotificationType.PROJECT_COMPLETED: emails.NotifyFollowersOnProjectCompletedEmail,
        NotificationType.COMMENT_ON_POST: emails.NotifyCreatorEmail,
        NotificationType.PROJECT_CREATED: emails.NotifyInitiatorsOnProjectCreatedEmail,
        NotificationType.PROJECT_DELETED: emails.NotifyInitiatorsOnProjectDeletedEmail,
        NotificationType.COMMENT_REPLY: emails.NotifyCreatorEmail,
        NotificationType.EVENT_ADDED: emails.NotifyFollowersOnEventAddedEmail,
        NotificationType.USER_CONTENT_CREATED: emails.NotifyModeratorsEmail,
        # TODO: Add missing mappings:
        # NotificationType.MODERATOR_HIGHLIGHT: emails.???,
        # NotificationType.EVENT_CANCELLED: emails.???,
        # NotificationType.EVENT_UPDATE: emails.???,
    }
    return email_map.get(notification_type)
