from ...models import Notification, NotificationType
from ..project import ProjectNotificationStrategy
from apps.users.models import User
from django.utils.translation import gettext_lazy as _

class OfflineEventReminderStrategy(ProjectNotificationStrategy):
    """Strategy for event reminder notifications"""
    
    def get_in_app_recipients(self, event):
        return self._get_event_recipients(event, NotificationType.EVENT_SOON, 'in_app')
    
    def get_email_recipients(self, event):
        return self._get_event_recipients(event, NotificationType.EVENT_SOON, 'email')
  
    def create_notification_data(self, event):
        time_format = "%B %d, %Y at %H:%M" if event.date else "%B %d, %Y"
        str_time = event_time.strftime(time_format) if event_time else _("soon")
        return {
            'notification_type': NotificationType.EVENT_SOON,
            'message_template': _("The event '{event}' in project {project} is starting on " + str_time),
            'context': {
                'project': event.project.name,
                'project_url': event.project.get_absolute_url(),
                'event': event.name,
                'event_url': event.get_absolute_url(),
            }
        }
