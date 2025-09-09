from ..project import ProjectNotificationStrategy
from ...models import NotificationType
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class ProjectStartedStrategy(ProjectNotificationStrategy):
    def get_in_app_recipients(self, phase):
        return self._get_project_recipients(phase, NotificationType.PROJECT_STARTED, 'in_app')
        
    def get_email_recipients(self, phase):
        return self._get_project_recipients(phase, NotificationType.PROJECT_STARTED, 'email')

    def create_notification_data(self, phase,) -> dict:
        project = phase.module.project
        return {
            'notification_type':  NotificationType.PROJECT_STARTED,
            'message_template': _("The project {project} has begun."),
            'context': {
                'project': project.name,
                'project_url': project.get_absolute_url(),
            },
        }