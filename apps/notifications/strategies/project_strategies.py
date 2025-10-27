from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..models import NotificationType
from .base import BaseNotificationStrategy

User = get_user_model()


class ProjectNotificationStrategy(BaseNotificationStrategy):
    """Base class for project-related notifications"""

    def _get_project_followers(self, project):
        """Get followers for a project - with optional caching"""
        return User.objects.filter(
            follow__project=project,
            follow__enabled=True,
        )

    def _get_project_initiators(self, project) -> List[User]:
        return project.organisation.initiators.all()

    def _get_project_moderators(self, project) -> List[User]:
        return project.moderators.all()

    def _get_project_recipients(self, project) -> List[User]:
        """Get all potential recipients for project notifications"""
        recipients_set = set()

        # Process followers
        followers = self._get_project_followers(project)
        recipients_set.update(followers)

        # Process initiators
        if hasattr(project, "organisation") and project.organisation:
            initiators = self._get_project_initiators(project)
            recipients_set.update(initiators)

        return list(recipients_set)

    def _get_event_recipients(self, event) -> List[User]:
        if not event.project:
            return []
        return self._get_project_recipients(event.project)

    def _get_phase_recipients(self, phase) -> List[User]:
        if not phase.module.project:
            return []
        return self._get_project_recipients(phase.module.project)


class ProjectStarted(ProjectNotificationStrategy):
    def get_recipients(self, project) -> List[User]:
        return self._get_project_recipients(project)

    def create_notification_data(self, project) -> dict:
        return {
            "notification_type": NotificationType.PROJECT_STARTED,
            "message_template": _("The project {project} has begun."),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
                "end_date": project.phases.filter(module__is_draft=False)
                .order_by(("end_date"))
                .first()
                .end_date,
            },
        }


class ProjectEnded(ProjectNotificationStrategy):
    def get_recipients(self, project) -> List[User]:
        return self._get_project_recipients(project)

    def create_notification_data(self, project) -> dict:
        return {
            "notification_type": NotificationType.PROJECT_COMPLETED,
            "message_template": _("The project {project} has been completed."),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
            },
        }


class ProjectInvitationReceived(ProjectNotificationStrategy):
    def get_recipients(self, invitation) -> List[User]:
        user_email = invitation.email
        try:
            user = User.objects.get(email=user_email)
            return [user]
        except User.DoesNotExist:
            return []

    def create_notification_data(self, invitation) -> dict:
        project = invitation.project
        return {
            "notification_type": NotificationType.PROJECT_INVITATION,
            "message_template": _("You have been invited to project {project}"),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
            },
        }


class ProjectModerationInvitationReceived(ProjectNotificationStrategy):
    def get_recipients(self, invitation) -> List[User]:
        user_email = invitation.email
        try:
            user = User.objects.get(email=user_email)
            return [user]
        except User.DoesNotExist:
            return []

    def create_notification_data(self, invitation) -> dict:
        project = invitation.project
        return {
            "notification_type": NotificationType.PROJECT_MODERATION_INVITATION,
            "message_template": _(
                "You have been invited to be a moderator of project {project}"
            ),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
            },
        }


class ProjectCreated(ProjectNotificationStrategy):
    def get_recipients(self, project) -> List[User]:
        print("getting recipients for project")
        recips = self._get_project_initiators(project)
        print(len(recips))
        return recips

    def create_notification_data(self, project) -> dict:
        return {
            "notification_type": NotificationType.PROJECT_CREATED,
            "message_template": _("A new project {project} has been created."),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
                "organisation": project.organisation.name,
            },
        }


class ProjectDeleted(ProjectNotificationStrategy):
    def get_recipients(self, project) -> List[User]:
        return self._get_project_initiators(project)

    def create_notification_data(self, project) -> dict:
        return {
            "notification_type": NotificationType.PROJECT_DELETED,
            "message_template": _("The project {project} has been deleted."),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
                "site_name": "aplus",  # TODO: use get_current_site or similar
            },
        }


class UserContentCreated(ProjectNotificationStrategy):
    """Handle notifying moderators when a new Idea/MapIdea/Proposal posted on project"""

    def __init__(self, content_type=None):
        self.content_type = content_type
        super().__init__()

    def get_recipients(self, obj) -> List[User]:
        return self._get_project_moderators(obj.project)

    def create_notification_data(self, obj) -> dict:
        print("CREATING A NOTIFICATION --------->>>>")
        # Auto-detect content type from object class if not provided
        content_type = self.content_type or obj.__class__.__name__

        return {
            "notification_type": NotificationType.USER_CONTENT_CREATED,
            "message_template": _(
                'A new {content_type} "{content}" has been created in project {project}.'
            ),
            "context": {
                "project": obj.project.name,
                "project_url": obj.project.get_absolute_url(),
                "organisation": obj.project.organisation.name,
                "content_type": content_type.lower(),  # "idea", "mapidea", "proposal"
                "content_type_display": content_type,  # "Idea", "MapIdea", "Proposal"
                "content": obj.name,
                "content_url": obj.get_absolute_url(),
                "creator_name": obj.creator.username,
            },
        }
