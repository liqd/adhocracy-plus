from django.apps import apps

from .models import NotificationType


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
        NotificationType.USER_ENGAGEMENT: emails.NotifyCreatorEmail,
        # NotificationType.COMMENT_REPLY: emails.NotifyCommentReplyEmail,
        NotificationType.MODERATOR_IDEA_FEEDBACK: emails.NotifyCreatorOnModeratorFeedback,
        NotificationType.MODERATOR_BLOCKED_COMMENT: emails.NotifyCreatorOnModeratorBlocked,
        NotificationType.EVENT_SOON: emails.NotifyFollowersOnUpcomingEventEmail,
        # TODO: Add missing mappings:
        # NotificationType.COMMENT_ON_POST: emails.???,
        # NotificationType.MODERATOR_HIGHLIGHT: emails.???,
        # NotificationType.EVENT_CANCELLED: emails.???,
        # NotificationType.EVENT_ADDED: emails.???,
        # NotificationType.EVENT_UPDATE: emails.???,
        # NotificationType.PROJECT_STARTED: emails.???,
        # NotificationType.PROJECT_COMPLETED: emails.???,
    }
    return email_map.get(notification_type)
