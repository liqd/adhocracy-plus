from .project_strategies import ProjectNotificationStrategy
from ..models import NotificationType
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class PhaseStarted(ProjectNotificationStrategy):
    def get_in_app_recipients(self, phase):
        return self._get_phase_recipients(phase, NotificationType.PHASE_STARTED, 'in_app')
        
    def get_email_recipients(self, phase):
        return self._get_phase_recipients(phase, NotificationType.PHASE_STARTED, 'email')

    # TODO: Check if phases have urls, or which url is best to use
    def create_notification_data(self, phase,) -> dict:
        project = phase.module.project
        return {
            'notification_type':  NotificationType.PHASE_STARTED,
            'message_template': _("The phase '{phase}' in {project} has begun."),
            'context': {
                'phase': phase.name,
                'phase_url': phase.get_absolute_url() if hasattr(phase, 'get_absolute_url') else project.get_absolute_url(),
                'project': project.name,
                'project_url': project.get_absolute_url(),
            },
        }

class PhaseEnded(ProjectNotificationStrategy):
    def get_in_app_recipients(self, phase):
        return self._get_phase_recipients(phase, NotificationType.PHASE_ENDED, 'in_app')
        
    def get_email_recipients(self, phase):
        return self._get_phase_recipients(phase, NotificationType.PHASE_ENDED, 'email')

    # TODO: Check message, phase URL 
    def create_notification_data(self, phase) -> dict:
        project = phase.module.project
        return {
            'notification_type': NotificationType.PHASE_ENDED,
            'message_template': _("The phase '{phase}' in {project} has been completed"),
            'context': {
                'phase': phase.name,
                'phase_url': phase.get_absolute_url() if hasattr(phase, 'get_absolute_url') else project.get_absolute_url(),
                'project': project.name,
                'project_url': project.get_absolute_url(),
            },
        }