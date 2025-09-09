from ..project import ProjectNotificationStrategy
from ...models import NotificationType
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class ProjectInvitationReceivedStrategy(ProjectNotificationStrategy):
    def get_in_app_recipients(self, invitation):
        user_email = invitation.email
        user = User.objects.get(email=user_email)
        return [user]
        
    def get_email_recipients(self, invitation):
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