from django.contrib.auth import get_user_model
from ...models import NotificationType
from ..project import ProjectNotificationStrategy
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class OfflineEventCreatedStrategy(ProjectNotificationStrategy):
    """Strategy for notifications when an offline event is added to a project"""
    
    def get_in_app_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event, NotificationType.EVENT_ADDED, 'in_app')
    
    def get_email_recipients(self, event) -> list[User]:
        return self._get_event_recipients(event, NotificationType.EVENT_ADDED, 'email')
    
    def create_notification_data(self, offline_event):
        """Create notification data for offline events"""
        
        return {
            'notification_type': NotificationType.EVENT_ADDED,
            'title': _("New event in {}").format(offline_event.project.name),
            'message_template': _("A new event '{event}' has been added to the project {project}"),
            'context': {
                'project': offline_event.project.name,
                'project_url': offline_event.project.get_absolute_url(),
                'event': offline_event.name,
                'event_url': offline_event.get_absolute_url(),
            }
        }