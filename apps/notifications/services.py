from typing import List

from django.apps import apps

from .constants import EMAIL_CLASS_MAPPING
from .models import NotificationSettings


class NotificationService:
    """Service layer for notification creation and delivery"""

    @staticmethod
    def create_notifications(obj, strategy) -> None:
        """
        Orchestrate notification creation and delivery

        Args:
            obj: The object that triggered the notification
            strategy: Notification strategy implementing get_recipients() and create_notification_data()
        """
        Notification = apps.get_model("a4_candy_notifications", "Notification")
        notification_data = strategy.create_notification_data(obj)
        notification_type = notification_data["notification_type"]

        # Get ALL potential recipients (no preference filtering)
        all_recipients = strategy.get_recipients(obj)

        # Filter by notification preferences per channel
        in_app_recipients = NotificationService._filter_recipients_by_preferences(
            all_recipients, notification_type, "in_app"
        )
        email_recipients = NotificationService._filter_recipients_by_preferences(
            all_recipients, notification_type, "email"
        )

        # Create in-app notifications
        notifications = []
        for recipient in in_app_recipients:
            notifications.append(Notification(recipient=recipient, **notification_data))

        if notifications:
            Notification.objects.bulk_create(notifications)

        # Send emails
        if email_recipients:
            NotificationService._send_email_notifications(
                email_recipients, obj, strategy, notification_data
            )

    @staticmethod
    def _filter_recipients_by_preferences(
        recipients: List, notification_type: str, channel: str
    ) -> List:
        """
        Filter recipients based on their notification preferences

        Args:
            recipients: List of potential recipients
            notification_type: Type of notification
            channel: Delivery channel ("in_app" or "email")

        Returns:
            Filtered list of recipients who want this notification type
        """
        filtered = []
        for recipient in recipients:
            settings = NotificationSettings.get_for_user(recipient)
            if settings.should_receive_notification(notification_type, channel):
                filtered.append(recipient)
        return filtered

    @staticmethod
    def _send_email_notifications(recipients, obj, strategy, notification_data):
        try:
            email_class = NotificationService._map_notification_type_to_email_class(
                notification_data["notification_type"]
            )

            if email_class:
                recipient_ids = [
                    recipient.id if hasattr(recipient, "id") else recipient
                    for recipient in recipients
                ]
                email_class.send(
                    obj,
                    strategy_recipient_ids=recipient_ids,
                    notification_data=notification_data,
                )

        except ValueError as e:
            # Log the error but don't crash the entire notification process
            print(f"Failed to send email notification: {e}")

    @staticmethod
    def _map_notification_type_to_email_class(notification_type: str):
        """
        Map notification type to appropriate email class

        Args:
            notification_type: Type of notification

        Returns:
            Email class

        Raises:
            ValueError: If no email class is mapped for the notification type
        """
        email_class = EMAIL_CLASS_MAPPING.get(notification_type)
        if not email_class:
            print(f"No email class mapped for notification type: {notification_type}")
            # raise ValueError(
            #     f"No email class mapped for notification type: {notification_type}"
            # )

        return email_class
