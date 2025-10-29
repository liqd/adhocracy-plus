from typing import List

from django.apps import apps
from django.template.loader import render_to_string

from adhocracy4.emails.mixins import SyncEmailMixin
from apps.users.emails import EmailAplus as Email

from .models import NOTIFICATION_TYPE_MAPPING
from .models import NotificationCategory
from .models import NotificationSettings


class NotificationEmail(SyncEmailMixin, Email):
    """Email class for notification emails"""

    template_name = "a4_candy_notifications/emails/strategy_email_base"

    def __init__(self, email_context, organisation, recipients):
        self._email_context = email_context
        self._organisation = organisation
        self._recipients = recipients

    def get_organisation(self):
        return self._organisation

    def get_receivers(self):
        print("SENDING TO X RECEIVERS", len(self._recipients))
        return self._recipients

    def render(self, template_name, context):
        # Add our email context
        context.update(self._email_context)

        if "content_template" in context:
            content_template = context.pop("content_template")
            context["content"] = render_to_string(content_template, context)

        # Interpolate receiver variables
        receiver = context.get("receiver")
        if receiver:
            if "subject" in context:
                context["subject"] = context["subject"].format(
                    site_name=(
                        context.get("site", "").name if context.get("site") else ""
                    ),
                    project_name=context.get("project"),
                )
            if "greeting" in context:
                context["greeting"] = context["greeting"].format(
                    receiver_name=receiver.username
                )
            if "reason" in context:
                context["reason"] = context["reason"].format(
                    receiver_email=receiver.email,
                    organisation_name=context.get("organisation_name", ""),
                    site_name=(
                        context.get("site", "").name if context.get("site") else ""
                    ),
                )

        return super().render(template_name, context)


class NotificationService:
    """Service layer for notification creation and delivery"""

    @staticmethod
    def create_notifications(obj, strategy) -> None:
        """
        Orchestrate notification creation and delivery
        """
        Notification = apps.get_model("a4_candy_notifications", "Notification")
        notification_data = strategy.create_notification_data(obj)
        notification_type = notification_data["notification_type"]

        # Get ALL potential recipients
        all_recipients = strategy.get_recipients(obj)

        # Filter recipients by preferences
        in_app_recipients, email_recipients = (
            NotificationService._get_filtered_recipients(
                all_recipients, notification_type
            )
        )

        # Send emails
        if email_recipients:
            email_context = notification_data.get("email_context", {})
            organisation = strategy.get_organisation(obj)

            email = NotificationEmail(
                email_context=email_context,
                organisation=organisation,
                recipients=email_recipients,
            )
            email.dispatch(obj)
        # Remove email_context before creating notifications
        notification_data.pop("email_context", None)

        # Create in-app notifications
        notifications = [
            Notification(recipient=recipient, **notification_data)
            for recipient in in_app_recipients
        ]

        if notifications:
            Notification.objects.bulk_create(notifications)

    @staticmethod
    def _get_filtered_recipients(all_recipients, notification_type):
        """
        Get filtered recipients for both channels
        """
        should_check_preferences = (
            NOTIFICATION_TYPE_MAPPING[notification_type]
            != NotificationCategory.MODERATION
        )

        if not should_check_preferences:
            return all_recipients, all_recipients

        in_app_recipients = NotificationService._filter_recipients_by_preferences(
            all_recipients, notification_type, "in_app"
        )
        email_recipients = NotificationService._filter_recipients_by_preferences(
            all_recipients, notification_type, "email"
        )

        return in_app_recipients, email_recipients

    @staticmethod
    def _filter_recipients_by_preferences(
        recipients: List, notification_type: str, channel: str
    ) -> List:
        """
        Filter recipients based on their notification preferences
        """
        filtered = []
        for recipient in recipients:
            settings = NotificationSettings.get_for_user(recipient)
            if settings.should_receive_notification(notification_type, channel):
                filtered.append(recipient)
        return filtered
