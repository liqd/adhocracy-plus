from .base import BaseNotificationStrategy
from abc import abstractmethod
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from ..models import NotificationType
from typing import List

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
    
    def get_in_app_recipients(self, project) -> List[User]:
        return self._get_project_recipients(project, NotificationType.PROJECT_STARTED, 'in_app')
    
    def get_email_recipients(self, project) -> List[User]:
        return self._get_project_recipients(project, NotificationType.PROJECT_STARTED, 'email')
    
    def _get_project_recipients(self, project, notification_type, channel) -> List[User]:
        followers = self._get_project_followers(project)
        return [
            user for user in followers 
            if user.notification_settings.should_receive_notification(notification_type, channel)
        ]

    def _get_event_recipients(self, event, notification_type, channel) -> List[User]:
        if not event.project:
            return []
        project = event.project
        recipients = self._get_project_recipients(project, notification_type, channel)
        return recipients

    def _get_phase_recipients(self, phase, notification_type, channel) -> List[User]:
        if not phase.module.project:
            return []
        project = phase.module.project
        recipients = self._get_project_recipients(project, notification_type, channel)
        return recipients


class ProjectStarted(ProjectNotificationStrategy):
    def get_in_app_recipients(self, phase) -> List[User]:
        return self._get_phase_recipients(phase, NotificationType.PROJECT_STARTED, 'in_app')
        
    def get_email_recipients(self, phase) -> List[User]:
        return self._get_phase_recipients(phase, NotificationType.PROJECT_STARTED, 'email')

    def create_notification_data(self, phase) -> dict:
        project = phase.module.project
        return {
            'notification_type':  NotificationType.PROJECT_STARTED,
            'message_template': _("The project {project} has begun."),
            'context': {
                'project': project.name,
                'project_url': project.get_absolute_url(),
            },
        }

class ProjectEnded(ProjectNotificationStrategy):
    def get_in_app_recipients(self, project) -> List[User]:
        return self._get_project_recipients(project, NotificationType.PROJECT_COMPLETED, 'in_app')
        
    def get_email_recipients(self, project) -> List[User]:
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

class ProjectInvitationReceived(ProjectNotificationStrategy):
    def get_in_app_recipients(self, invitation) -> List[User]:
        user_email = invitation.email
        try:
            user = User.objects.get(email=user_email)
            return [user]
        except User.DoesNotExist:
            return []
        
    def get_email_recipients(self, invitation) -> List[User]:
        return []

    def create_notification_data(self, invitation) -> dict:
        project = invitation.project
        return {
            'notification_type':  NotificationType.PROJECT_INVITATION,
            'message_template': _("You have been invited to project {project}"),
            'context': {
                'project': project.name,
                'project_url': project.get_absolute_url(),
            },
        }