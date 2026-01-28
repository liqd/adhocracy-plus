from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..models import NotificationType
from .base import BaseNotificationStrategy

User = get_user_model()


class ProjectNotificationStrategy(BaseNotificationStrategy):
    """Base class for project-related notifications"""

    def get_organisation(self, project):
        return project.organisation

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
        end_date = (
            project.phases.filter(module__is_draft=False)
            .order_by("end_date")
            .first()
            .end_date
        )

        email_context = {
            "subject": _("Here we go: {project_name} starts now!").format(
                project_name=project.name
            ),
            "headline": _("Here we go!"),
            "subheadline": project.name,
            "cta_url": project.get_absolute_url(),
            "cta_label": _("Join now"),
            "reason": _(
                "This email was sent to {receiver_email}. You have received the e-mail because you are following the above project."
            ),
            "content_template": "a4_candy_notifications/emails/content/project_started.en.email",
            "project_name": project.name,
            "end_date": end_date,
        }

        return {
            "notification_type": NotificationType.PROJECT_STARTED,
            "message_template": "The project {project} has begun.",
            "translated_message_template": _("The project {project} has begun."),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
                "end_date": end_date,
            },
            "email_context": email_context,
        }


class ProjectEnded(ProjectNotificationStrategy):
    def get_recipients(self, project) -> List[User]:
        return self._get_project_recipients(project)

    def create_notification_data(self, project) -> dict:
        email_context = {
            "subject": _("{project_name} has completed.").format(
                project_name=project.name
            ),
            "subheadline": project.name,
            "cta_url": project.get_absolute_url(),
            "cta_label": _("View now"),
            "reason": _(
                "This email was sent to {receiver_email}. You have received the e-mail because you are following the above project."
            ),
            "content_template": "a4_candy_notifications/emails/content/project_ended.en.email",
            "project": project.name,
        }

        return {
            "notification_type": NotificationType.PROJECT_COMPLETED,
            "message_template": "The project {project} has been completed.",
            "translated_message_template": _(
                "The project {project} has been completed."
            ),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
            },
            "email_context": email_context,
        }


class ProjectInvitationCreated(ProjectNotificationStrategy):
    def get_organisation(self, invitation):
        return invitation.project.organisation

    def get_recipients(self, invitation) -> List[User]:
        user_email = invitation.email
        try:
            user = User.objects.get(email=user_email)
            return [user]
        except User.DoesNotExist:
            return []

    def create_notification_data(self, invitation) -> dict:
        project = invitation.project
        is_semipublic = getattr(project, "is_semipublic", False)
        project_type = "semi-public" if is_semipublic else "private"

        email_context = {
            "subject": _(
                "Invitation to the {project_type} project: {project_name}"
            ).format(project_type=project_type, project_name=project.name),
            "headline": _(
                'Invitation to the {project_type} project: "{project_name}"'
            ).format(project_type=project_type, project_name=project.name),
            "cta_url": f"{invitation.get_absolute_url()}",
            "cta_label": _("Accept invitation"),
            "reason": _("This email was sent to {receiver_email}."),
            "content_template": "a4_candy_notifications/emails/content/project_invitation.en.email",
            "participantinvite": invitation,
            "project": project,
            "project_name": project.name,
            "project_type": project_type,
            "site": invitation.site,
        }

        return {
            "notification_type": NotificationType.PROJECT_INVITATION,
            "message_template": "You have been invited to project {project}. Please check your email to accept.",
            "translated_message_template": _(
                "You have been invited to project {project}. Please check your email to accept."
            ),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
                "project_type": project_type,
            },
            "email_context": email_context,
        }


class ProjectModerationInvitationReceived(ProjectNotificationStrategy):

    def get_organisation(self, invitation):
        return invitation.project.organisation

    def get_recipients(self, invitation) -> List[User]:
        user_email = invitation.email
        try:
            user = User.objects.get(email=user_email)
            return [user]
        except User.DoesNotExist:
            return []

    def create_notification_data(self, invitation) -> dict:
        project = invitation.project
        email_context = {
            "subject": _("Moderator invitation for project {project_name}").format(
                project_name=project.name
            ),
            "headline": _("Moderator Invitation"),
            "cta_url": invitation.get_absolute_url(),
            "cta_label": _("View Invitation"),
            "reason": _("This email was sent to {receiver_email}."),
            "content_template": "a4_candy_notifications/emails/content/project_moderation_invitation.en.email",
            "project_name": project.name,
        }
        translated = _(
            "You have been invited to be a moderator of project {project_name}. View {invitation}"
        )
        return {
            "notification_type": NotificationType.PROJECT_MODERATION_INVITATION,
            "message_template": "You have been invited to be a moderator of project {project_name}. View {invitation}",
            "translated_message_template": _(
                "You have been invited to be a moderator of project {project_name}. View {invitation}"
            ),
            "context": {
                "project_name": project.name,
                "invitation": "invitation",
                "invitation_url": invitation.get_absolute_url(),
                "project_url": None,  # Explicitly no project link
                "irrelevant": translated,  # translation hack, to remove
            },
            "email_context": email_context,
        }


class ProjectCreated(ProjectNotificationStrategy):
    def get_recipients(self, project) -> List[User]:
        return self._get_project_initiators(project)

    def create_notification_data(self, project) -> dict:
        email_context = {
            "subject": _("New project {project_name} on {site_name}"),
            "headline": _(
                "The new project {project_name} was created for {organisation_name}"
            ).format(
                project_name=project.name, organisation_name=project.organisation.name
            ),
            "cta_url": project.get_absolute_url(),
            "cta_label": _("Show project"),
            "reason": _(
                "This email was sent to {receiver_email}. This email was sent to you because you are an initiator of {organisation_name}."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/project_created.en.email",
            # Template variables
            "project_name": project.name,
            "organisation_name": project.organisation.name,
        }

        return {
            "notification_type": NotificationType.PROJECT_CREATED,
            "message_template": "A new project {project} has been created.",
            "translated_message_template": _(
                "A new project {project} has been created."
            ),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
                "organisation": project.organisation.name,
            },
            "email_context": email_context,
        }


class ProjectDeleted(ProjectNotificationStrategy):
    def get_recipients(self, project) -> List[User]:
        return self._get_project_initiators(project)

    def create_notification_data(self, project) -> dict:
        email_context = {
            "subject": _("Deletion of project"),
            "headline": _("The project {project} was deleted.").format(
                project=project.name
            ),
            "reason": _(
                "This email was sent to {receiver_email}. This email was sent to you because you are an initiator of the organisation '{organisation_name}', in which a project was deleted."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/project_deleted.en.email",
            # Template variables
            "project": project.name,
            "organisation": project.organisation.name,
            "site": project.organisation.site,
        }

        return {
            "notification_type": NotificationType.PROJECT_DELETED,
            "message_template": "The project {project} has been deleted.",
            "translated_message_template": _("The project {project} has been deleted."),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
                "organisation": project.organisation.name,
            },
            "email_context": email_context,
        }


class UserContentCreated(ProjectNotificationStrategy):
    """Handle notifying moderators when a new Idea/MapIdea/Proposal posted on project"""

    def __init__(self, content_type=None):
        self.content_type = content_type
        super().__init__()

    def get_organisation(self, obj):
        return obj.project.organisation

    def get_recipients(self, obj) -> List[User]:
        return self._get_project_moderators(obj.project)

    def create_notification_data(self, obj) -> dict:
        content_type = self.content_type or obj.__class__.__name__
        content_type_display = content_type
        content_type_article = "A"
        if content_type_display[0].lower() in ["a", "e", "i", "o", "u"]:
            content_type_article = "An"
        email_context = {
            "subject": _(
                "{article} {content_type} was added to the project {project}"
            ).format(
                article=content_type_article,
                content_type=content_type_display,
                project=obj.project.name,
            ),
            "headline": _(
                "{creator_name} created {article} {content_type} on the project {project}"
            ).format(
                article=content_type_article.lower(),
                creator_name=obj.creator.username,
                content_type=content_type_display,
                project=obj.project.name,
            ),
            "cta_url": obj.get_absolute_url(),
            "cta_label": _("Check the {content_type}").format(
                content_type=content_type_display
            ),
            "reason": _(
                "This email was sent to {receiver_email}. This email was sent to you because you are a moderator in the project."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/user_content_created.en.email",
            # Template variables
            "project": obj.project.name,
            "creator_name": obj.creator.username,
            "content_type": content_type.lower(),
            "content_type_display": content_type_display,
            "content_url": obj.get_absolute_url(),
            "site": obj.project.organisation.site,
        }

        return {
            "notification_type": NotificationType.USER_CONTENT_CREATED,
            "message_template": 'A new {content_type} "{content}" has been created in project {project}.',
            "translated_message_template": _(
                'A new {content_type} "{content}" has been created in project {project}.'
            ),
            "context": {
                "project": obj.project.name,
                "project_url": obj.project.get_absolute_url(),
                "organisation": obj.project.organisation.name,
                "content_type": content_type.lower(),
                "content_type_display": content_type_display,
                "content": obj.name,
                "content_url": obj.get_absolute_url(),
                "creator_name": obj.creator.username,
            },
            "email_context": email_context,
        }
