from .base import BaseNotificationStrategy
from abc import abstractmethod
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectNotificationStrategy(BaseNotificationStrategy):
    """Base class for project-related notifications"""
    
    def _get_project_followers(self, project):
        """Get followers for a project - with optional caching"""
        # Consider whether caching is appropriate here
        # User preferences might change frequently
        return User.objects.filter(
            follow__project=project,
            follow__enabled=True,
        ).prefetch_related('notification_settings')
    
    def get_in_app_recipients(self, project) -> list[User]:
        return self._get_recipients(project, 'in_app')
    
    def get_email_recipients(self, project) -> list[User]:
        return self._get_recipients(project, 'email')
    
    def _get_project_recipients(self, project, notification_type, channel):
        followers = self._get_project_followers(project)
        return [
            user for user in followers 
            if user.notification_settings.should_receive_notification(notification_type, channel)
        ]

    def _get_event_recipients(self, event, notification_type, channel):
        if not event.project:
            return []
        project = event.project
        recipients = self._get_project_recipients(project, notification_type, channel)
        return recipients

    def _get_phase_recipients(self, phase, notification_type, channel):
        if not phase.module.project:
            return []
        project = phase.module.project
        recipients = self._get_project_recipients(project, notification_type, channel)
        return recipients

class ProjectCompletedStrategy(ProjectNotificationStrategy):
    def get_in_app_recipients(self, project):
        return self._get_project_recipients(phase, NotificationType.PROJECT_COMPLETED, 'in_app')
        
    def get_email_recipients(self, project):
        return self._get_project_recipients(event, NotificationType.PROJECT_COMPLETED, 'email')

    # TODO: Check if phases have urls, or which url is best to use
    def create_notification_data(self, project) -> dict:
        return {
            'message_template': _("The project {project} is complete."),
            'context': {
                'project': project.name,
                'project_url': project.get_absolute_url(),
            },
        }