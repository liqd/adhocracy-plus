from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from ..models import NotificationType
from .project_strategies import ProjectNotificationStrategy

User = get_user_model()


class OfflineEventCreated(ProjectNotificationStrategy):
    """Strategy for notifications when an offline event is added to a project"""

    def get_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event)

    def create_notification_data(self, offline_event):
        """Create notification data for offline events"""
        time_format = "%B %d, %Y at %H:%M" if offline_event.date else "%B %d, %Y"
        try:
            str_time = (
                offline_event.date.strftime(time_format)
                if offline_event.date
                else _("soon")
            )
        except AttributeError:
            str_time = offline_event.date if offline_event.date else _("soon")

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
                "event_date": str_time,
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
        if offline_event.date:
            # Use Django's timezone-aware formatting
            if offline_event.date.time() == timezone.datetime.min.time():
                # Date only (no specific time)
                str_time = date_format(offline_event.date, "DATE_FORMAT")
            else:
                # Date with time
                str_time = date_format(
                    timezone.localtime(offline_event.date), "DATETIME_FORMAT"
                )
        else:
            str_time = _("soon")

        return {
            "notification_type": NotificationType.EVENT_SOON,
            "message_template": _(
                "The event '{event}' in project {project} is starting on {date}"
            ),
            "context": {
                "project": offline_event.project.name,
                "project_url": offline_event.project.get_absolute_url(),
                "organisation": offline_event.project.organisation.name,
                "event": offline_event.name,
                "event_url": offline_event.get_absolute_url(),
                "event_date": str_time,
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
