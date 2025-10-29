from typing import List

from django.apps import apps

from adhocracy4.emails.mixins import SyncEmailMixin
from apps.users.emails import EmailAplus as Email

from .constants import EMAIL_CLASS_MAPPING
from .models import NOTIFICATION_TYPE_MAPPING
from .models import NotificationCategory
from .models import NotificationSettings


class NotificationEmail(SyncEmailMixin, Email):
    """Email class for notification emails"""

    template_name = "a4_candy_notifications/emails/strategy_email_base"

    def __init__(self, notification_object, email_context, organisation):
        self.object = notification_object
        self.email_context = email_context
        self._organisation = organisation

    def get_organisation(self):
        return self._organisation

    def get_receivers(self):
        return self.email_context.get("recipients", [])

    def get_context(self):
        context = super().get_context()
        context.update(self.email_context)
        return context


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

        should_check_preferences = (
            NOTIFICATION_TYPE_MAPPING[notification_type]
            != NotificationCategory.MODERATION
        )

        if should_check_preferences:
            # Filter by notification preferences per channel
            in_app_recipients = NotificationService._filter_recipients_by_preferences(
                all_recipients, notification_type, "in_app"
            )
            email_recipients = NotificationService._filter_recipients_by_preferences(
                all_recipients, notification_type, "email"
            )
        else:
            in_app_recipients = all_recipients
            email_recipients = all_recipients

        #    Send emails
        if email_recipients:
            NotificationService._send_email_notifications(
                email_recipients, obj, strategy, notification_data
            )

        # remove email_context from notification
        notification_data.pop("email_context", None)

        # Create in-app notifications
        notifications = []
        for recipient in in_app_recipients:
            notifications.append(Notification(recipient=recipient, **notification_data))

        if notifications:
            Notification.objects.bulk_create(notifications)

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
        """
        Send email notifications to recipients
        """
        # Get email context from strategy
        email_context = NotificationService.get_email_context(notification_data)
        email_context["recipients"] = recipients

        # Get organisation from strategy
        organisation = strategy.get_organisation(obj)

        # Create and send email using the existing pattern
        email = NotificationEmail(obj, email_context, organisation)
        email.dispatch(obj)

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

    def get_email_context(notification_data):
        """Extract email template variables from notification email_context"""
        email_context = notification_data.get("email_context", {})

        # Map email_* keys to the template variable names
        return {
            "subject": email_context.get("email_subject", ""),
            "headline": email_context.get("email_headline", ""),
            "subheadline": email_context.get("email_subheadline", ""),
            "greeting": email_context.get("email_greeting", ""),
            "content": email_context.get("email_content", ""),
            "cta_url": email_context.get("email_cta_url", ""),
            "cta_label": email_context.get("email_cta_label", ""),
            "reason": email_context.get("email_reason", ""),
            # Additional context
            "project_name": email_context.get("project_name", ""),
            "commenter_name": email_context.get("commenter_name", ""),
            "comment_text": email_context.get("comment_text", ""),
            "parent_comment_text": email_context.get("parent_comment_text", ""),
            "comment_url": email_context.get("email_cta_url", ""),
        }
