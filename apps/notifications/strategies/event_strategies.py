from django.contrib.auth import get_user_model
from ..models import NotificationType
from .project_strategies import ProjectNotificationStrategy
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class OfflineEventCreated(ProjectNotificationStrategy):
    """Strategy for notifications when an offline event is added to a project"""
    
    def get_in_app_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event, NotificationType.EVENT_ADDED, 'in_app')
    
    def get_email_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event, NotificationType.EVENT_ADDED, 'email')
    
    def create_notification_data(self, offline_event):
        """Create notification data for offline events"""
        
        return {
            'notification_type': NotificationType.EVENT_ADDED,
            'message_template': _("A new event '{event}' has been added to the project {project}"),
            'context': {
                'project': offline_event.project.name,
                'project_url': offline_event.project.get_absolute_url(),
                'event': offline_event.name,
                'event_url': offline_event.get_absolute_url(),
            }
        }

class OfflineEventDeleted(ProjectNotificationStrategy):
    """Strategy for event reminder notifications"""
    
    def get_in_app_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event, NotificationType.EVENT_CANCELLED, 'in_app')
    
    def get_email_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event, NotificationType.EVENT_CANCELLED, 'email')
    
    def create_notification_data(self, offline_event):
        return {
            'notification_type': NotificationType.EVENT_CANCELLED,
            # TODO: Check text here and remove event link, doen't make sense due to carousel
            'message_template': _("The event '{event}' in project {project} has been cancelled"),
            'context': {
                'project': offline_event.project.name,
                'project_url': offline_event.project.get_absolute_url(),
                'event': offline_event.name,
                'event_url': offline_event.get_absolute_url(),
            }
        }

class OfflineEventReminder(ProjectNotificationStrategy):
    """Strategy for event reminder notifications"""
    
    def get_in_app_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event, NotificationType.EVENT_SOON, 'in_app')
    
    def get_email_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event, NotificationType.EVENT_SOON, 'email')
  
    def create_notification_data(self, offline_event):
        time_format = "%B %d, %Y at %H:%M" if event.date else "%B %d, %Y"
        str_time = event_time.strftime(time_format) if event_time else _("soon")
        return {
            'notification_type': NotificationType.EVENT_SOON,
            'message_template': _("The event '{event}' in project {project} is starting on " + str_time),
            'context': {
                'project': offline_event.project.name,
                'project_url': offline_event.project.get_absolute_url(),
                'event': offline_event.name,
                'event_url': offline_event.get_absolute_url(),
            }
        }

class OfflineEventUpdate(ProjectNotificationStrategy):
    def get_in_app_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event, NotificationType.EVENT_UPDATE, 'in_app')
    
    def get_email_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event, NotificationType.EVENT_UPDATE, 'email')
    
    
    def create_notification_data(self, offline_event, update_type='rescheduled', old_data=None):
        return {
            'notification_type': NotificationType.EVENT_UPDATE,
            'message_template': _("The event {event} in project {project} has been updated"),
            'context': {
                'project': offline_event.project.name if event.project else '',
                'project_url': offline_event.project.get_absolute_url() if offline_event.project else '#',
                'event': offline_event.name,
                'event_url': offline_event.get_absolute_url() if hasattr(event, 'get_absolute_url') else '#',
            }
        }