from ..project import ProjectNotificationStrategy
from ...models import NotificationType
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class ProjectEndedStrategy(ProjectNotificationStrategy):
    def get_in_app_recipients(self, project):
        return self._get_project_recipients(project, NotificationType.PROJECT_COMPLETED, 'in_app')
        
    def get_email_recipients(self, project):
        return self._get_project_recipients(project, NotificationType.PROJECT_COMPLETED, 'email')

    def create_notification_data(self, project) -> dict:
        return {
            'notification_type':  NotificationType.PROJECT_COMPLETED,
            'message_template': _("The project {project} has completed."),
            'context': {
                'project': project.name,
                'project_url': project.get_absolute_url(),
            },
        }