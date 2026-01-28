from typing import List

from django.apps import apps
from django.template.loader import render_to_string
from django.utils import translation

from apps.users.emails import EmailAplus as Email

from .models import NOTIFICATION_TYPE_MAPPING
from .models import NotificationCategory
from .models import NotificationSettings


class NotificationEmail(Email):
    """Email class for notification emails"""

    template_name = "a4_candy_notifications/emails/strategy_email_base"

    def __init__(self, email_context, organisation, recipients):
        self._email_context = email_context
        self._organisation = organisation
        self._recipients = recipients

    def get_organisation(self):
        return self._organisation

    def get_receivers(self):
        return self._recipients

    def render(self, template_name, context):
        language = self.get_receiver_language(context["receiver"])
        # Add our email context
        context.update(self._email_context)
        with translation.override(language):
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
                        event_name=context.get("event_name"),
                        project_name=context.get("project_name"),
                        project_type=context.get("project_type"),
                        article=context.get("article", ""),
                        content_type_display=context.get("content_type_display", ""),
                        commenter_name=context.get("commenter_name", ""),
                        post_name=context.get("post_name", ""),
                    )
                if "headline" in context:
                    context["headline"] = context["headline"].format(
                        project_name=context.get(
                            "project_name", context.get("project_name", "")
                        ),
                        project_type=context.get("project_type", ""),
                        organisation_name=context.get("organisation_name", ""),
                        article=context.get("article", ""),
                        article_lower=context.get("article_lower", ""),
                        content_type=context.get("content_type", ""),
                        content_type_display=context.get("content_type_display", ""),
                        creator_name=context.get("creator_name", ""),
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
        all_recipients = list(set(strategy.get_recipients(obj)))

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
        notification_data.pop("translated_message_template", None)

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

        unique_recipients = list(set(all_recipients))
        should_check_preferences = (
            NOTIFICATION_TYPE_MAPPING[notification_type]
            != NotificationCategory.MODERATION
        )

        if not should_check_preferences:
            return unique_recipients, unique_recipients

        in_app_recipients = NotificationService._filter_recipients_by_preferences(
            unique_recipients, notification_type, "in_app"
        )
        email_recipients = NotificationService._filter_recipients_by_preferences(
            unique_recipients, notification_type, "email"
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
