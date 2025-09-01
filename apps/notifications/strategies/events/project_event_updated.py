from ...models import NotificationType
from django.utils.translation import gettext_lazy as _
from ..project import ProjectNotificationStrategy


class OfflineEventUpdateStrategy(ProjectNotificationStrategy):
    def get_in_app_recipients(self, event):
        return self._get_event_recipients(event, NotificationType.EVENT_UPDATE, 'in_app')
    
    def get_email_recipients(self, event):
        return self._get_event_recipients(event, NotificationType.EVENT_UPDATE, 'email')
    
    
    def create_notification_data(self, event, update_type='rescheduled', old_data=None):
        return {
            'notification_type': NotificationType.EVENT_UPDATE,
            'message_template': _("The event {event} in project {project} has been updated"),
            'context': {
                'project': event.project.name if event.project else '',
                'project_url': event.project.get_absolute_url() if event.project else '#',
                'event': event.name,
                'event_url': event.get_absolute_url() if hasattr(event, 'get_absolute_url') else '#',
            }
        }

