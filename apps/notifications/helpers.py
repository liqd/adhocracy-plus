from django.apps import apps


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
        "user_engagement": emails.NotifyCreatorEmail,
        "project_event": emails.NotifyFollowersOnUpcomingEventEmail,
        "comment_reply": emails.NotifyCommentReplyEmail,
        "moderator_idea_feedback": emails.NotifyCreatorOnModeratorFeedback,
        "moderator_blocked_comment": emails.NotifyCreatorOnModeratorBlocked,
        "event_soon": emails.NotifyFollowersOnUpcomingEventEmail,
        # missing:
        #     comment_on_post - a user commented on your post
        #     moderator_highlight - a moderator highlighted your comment
        #     event_cancelled
        #     event_added
        #     event_update
        #     project_started
        #     project_completed
    }
    return email_map.get(notification_type)
