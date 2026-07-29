from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..models import NotificationType
from .base import BaseNotificationStrategy

User = get_user_model()


class OrganisationNewProject(BaseNotificationStrategy):
    def get_organisation(self, project):
        return project.organisation

    def get_recipients(self, project):
        organisation = project.organisation
        return User.objects.filter(
            organisationfollow__organisation=organisation,
            organisationfollow__enabled=True,
        )

    def create_notification_data(self, project):
        organisation = project.organisation
        email_context = {
            "subject": _("New project was published by {organisation_name}"),
            "headline": _("New project was published by {organisation_name}"),
            "cta_url": project.get_absolute_url(),
            "cta_label": _("Show project"),
            "reason": _(
                "This email was sent to {receiver_email}. You have received the "
                "e-mail because you are following {organisation_name}. If you no "
                "longer want to receive notifications for the organisation, "
                '<a href="{organisation_url}" target="_blank">click here</a>.'
            ),
            "content_template": (
                "a4_candy_notifications/emails/content/"
                "organisation_new_project.en.email"
            ),
            "project_name": project.name,
            "organisation_name": organisation.name,
            "organisation_path": organisation.get_absolute_url(),
            "project_description": project.description,
        }

        return {
            "notification_type": NotificationType.ORGANISATION_NEW_PROJECT,
            "message_template": (
                "The organisation {organisation} has published a new project "
                "{project}."
            ),
            "translated_message_template": _(
                "The organisation {organisation} has published a new project "
                "{project}."
            ),
            "context": {
                "project": project.name,
                "project_url": project.get_absolute_url(),
                "organisation": organisation.name,
                "organisation_url": organisation.get_absolute_url(),
            },
            "target_url": project.get_absolute_url(),
            "email_context": email_context,
        }
