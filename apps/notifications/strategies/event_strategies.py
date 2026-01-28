from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..models import NotificationType
from ..utils import format_event_date
from .project_strategies import ProjectNotificationStrategy

User = get_user_model()


class OfflineEventCreated(ProjectNotificationStrategy):
    """Strategy for notifications when an offline event is added to a project"""

    def get_organisation(self, event):
        return event.project.organisation

    def get_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event)

    def create_notification_data(self, offline_event):
        email_context = {
            "subject": _("Event added to project {project_name}"),
            "headline": _("Event"),
            "subheadline": offline_event.name,
            "cta_url": offline_event.get_absolute_url(),
            "cta_label": _("Show Event"),
            "reason": _(
                "This email was sent to {receiver_email}. You have received the e-mail because you are following the above project."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/event_added.en.email",
            # Template variables
            "project": offline_event.project.name,
            "project_name": offline_event.project.name,
            "event": offline_event.name,
            "event_date": format_event_date(offline_event.date),
            "organisation": offline_event.project.organisation.name,
        }

        return {
            "notification_type": NotificationType.EVENT_ADDED,
            "message_template": "A new event '{event}' has been added to the project {project}",
            "translated_message_template": _(
                "A new event '{event}' has been added to the project {project}"
            ),
            "context": {
                "project": offline_event.project.name,
                "project_url": offline_event.project.get_absolute_url(),
                "organisation": offline_event.project.organisation.name,
                "event": offline_event.name,
                "event_url": offline_event.get_absolute_url(),
                "event_date": format_event_date(offline_event.date),
            },
            "email_context": email_context,
        }


class OfflineEventDeleted(ProjectNotificationStrategy):
    """Strategy for event reminder notifications"""

    def get_organisation(self, event):
        return event.project.organisation

    def get_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event)

    def create_notification_data(self, offline_event):
        email_context = {
            "subject": _("Event {event} in project {project} cancelled").format(
                event=offline_event.name, project=offline_event.project.name
            ),
            "headline": _("Event"),
            "subheadline": offline_event.name,
            "reason": _(
                "This email was sent to {receiver_email}. You have received the e-mail because you are following the above project."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/event_deleted.en.email",
            # Template variables
            "project": offline_event.project.name,
            "event": offline_event.name,
            "event_date": format_event_date(offline_event.date),
            "organisation": offline_event.project.organisation.name,
        }

        return {
            "notification_type": NotificationType.EVENT_CANCELLED,
            "message_template": "The event '{event}' in project {project} has been cancelled",
            "translated_message_template": _(
                "The event '{event}' in project {project} has been cancelled"
            ),
            "context": {
                "project": offline_event.project.name,
                "project_url": offline_event.project.get_absolute_url(),
                "event": offline_event.name,
                "event_url": offline_event.get_absolute_url(),
                "event_date": format_event_date(offline_event.date),
            },
            "email_context": email_context,
        }


class OfflineEventReminder(ProjectNotificationStrategy):
    """Strategy for event reminder notifications"""

    def get_organisation(self, event):
        return event.project.organisation

    def get_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event)

    def create_notification_data(self, offline_event):
        email_context = {
            "subject": _("Event in project {project_name}"),
            "headline": _("Event"),
            "subheadline": offline_event.name,
            "cta_url": offline_event.get_absolute_url(),
            "cta_label": _("Show Event"),
            "reason": _(
                "This email was sent to {receiver_email}. You have received the e-mail because you are following the above project."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/event_soon.en.email",
            # Template variables
            "project": offline_event.project.name,
            "project_name": offline_event.project.name,
            "event": offline_event.name,
            "event_date": format_event_date(offline_event.date),
            "organisation": offline_event.project.organisation.name,
        }

        return {
            "notification_type": NotificationType.EVENT_SOON,
            "message_template": "The event '{event}' in project {project} is starting on {event_date}",
            "translated_message_template": _(
                "The event '{event}' in project {project} is starting on {event_date}"
            ),
            "context": {
                "project": offline_event.project.name,
                "project_url": offline_event.project.get_absolute_url(),
                "organisation": offline_event.project.organisation.name,
                "event": offline_event.name,
                "event_url": offline_event.get_absolute_url(),
                "event_date": format_event_date(offline_event.date),
            },
            "email_context": email_context,
        }


class OfflineEventUpdate(ProjectNotificationStrategy):
    def get_organisation(self, event):
        return event.project.organisation

    def get_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event)

    def create_notification_data(self, offline_event):
        email_context = {
            "subject": _("Event {event_name} in project {project_name} updated"),
            "headline": _("Event"),
            "subheadline": offline_event.name,
            "reason": _(
                "This email was sent to {receiver_email}. You have received the e-mail because you are following the above project."
            ),
            "cta_url": offline_event.get_absolute_url(),
            "cta_label": _("Show Event"),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/event_updated.en.email",
            # Template variables
            "project": offline_event.project.name,
            "project_name": offline_event.project.name,
            "event": offline_event.name,
            "event_name": offline_event.name,
            "event_date": format_event_date(offline_event.date),
            "organisation": offline_event.project.organisation.name,
        }

        return {
            "notification_type": NotificationType.EVENT_UPDATE,
            "message_template": "The event {event} in project {project} has been updated",
            "translated_message_template": _(
                "The event {event} in project {project} has been updated"
            ),
            "context": {
                "project": offline_event.project.name,
                "project_url": offline_event.project.get_absolute_url(),
                "event": offline_event.name,
                "event_url": offline_event.get_absolute_url(),
                "event_date": format_event_date(offline_event.date),
            },
            "email_context": email_context,
        }
