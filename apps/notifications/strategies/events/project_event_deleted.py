from ...models import Notification, NotificationType
from ..project import ProjectNotificationStrategy
from apps.users.models import User
from django.utils.translation import gettext_lazy as _

class OfflineEventDeletedStrategy(ProjectNotificationStrategy):
    """Strategy for event reminder notifications"""
    
    def get_in_app_recipients(self, event):
        return self._get_event_recipients(event, NotificationType.EVENT_CANCELLED, 'in_app')
    
    def get_email_recipients(self, event):
        return self._get_event_recipients(event, NotificationType.EVENT_CANCELLED, 'email')
    
    def create_notification_data(self, event):
        return {
            'notification_type': NotificationType.EVENT_CANCELLED,
            # TODO: Check text here and remove event link, doen't make sense due to carousel
            'message_template': _("The event '{event}' in project {project} has been cancelled"),
            'context': {
                'project': event.project.name,
                'project_url': event.project.get_absolute_url(),
                'event': event.name,
                'event_url': event.get_absolute_url(),
            }
        }
