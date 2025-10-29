from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..models import NotificationType
from ..utils import format_event_date
from .project_strategies import ProjectNotificationStrategy

User = get_user_model()


class OfflineEventCreated(ProjectNotificationStrategy):
    """Strategy for notifications when an offline event is added to a project"""

    def get_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event)

    def create_notification_data(self, offline_event):
        return {
            "notification_type": NotificationType.EVENT_ADDED,
            "message_template": _(
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
        }


class OfflineEventDeleted(ProjectNotificationStrategy):
    """Strategy for event reminder notifications"""

    def get_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event)

    def create_notification_data(self, offline_event):
        return {
            "notification_type": NotificationType.EVENT_CANCELLED,
            "message_template": _(
                "The event '{event}' in project {project} has been cancelled"
            ),
            "context": {
                "project": offline_event.project.name,
                "project_url": offline_event.project.get_absolute_url(),
                "event": offline_event.name,
                "event_url": offline_event.get_absolute_url(),
            },
        }


class OfflineEventReminder(ProjectNotificationStrategy):
    """Strategy for event reminder notifications"""

    def get_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event)

    def create_notification_data(self, offline_event):
        return {
            "notification_type": NotificationType.EVENT_SOON,
            "message_template": _(
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
        }


class OfflineEventUpdate(ProjectNotificationStrategy):
    def get_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event)

    def create_notification_data(self, offline_event):
        return {
            "notification_type": NotificationType.EVENT_UPDATE,
            "message_template": _(
                "The event {event} in project {project} has been updated"
            ),
            "context": {
                "project": offline_event.project.name,
                "project_url": offline_event.project.get_absolute_url(),
                "event": offline_event.name,
                "event_url": offline_event.get_absolute_url(),
            },
        }
