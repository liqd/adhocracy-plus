from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.users.emails import EmailAplus as Email

User = get_user_model()


def _exclude_notifications_disabled(receivers, notification_field):
    if hasattr(receivers, "filter"):
        filters = {f"notification_settings__{notification_field}": True}
        return receivers.filter(**filters)
    return [
        user
        for user in receivers
        if getattr(user.notification_settings, notification_field)
    ]


class InviteParticipantEmail(Email):
    template_name = "a4_candy_projects/emails/invite_participant"

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        return [self.object.email]


class InviteModeratorEmail(Email):
    template_name = "a4_candy_projects/emails/invite_moderator"

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        return [self.object.email]


class WelcomeToPrivateProjectEmail(Email):
    template_name = "a4_candy_projects/emails/welcome_participant"

    def get_organisation(self):
        return self.object.organisation

    def get_receivers(self):
        participant_pks = self.kwargs["participant_pks"]
        receivers = User.objects.filter(pk__in=participant_pks)
        return receivers


class NotifyInitiatorsPublishResultsEmail(Email):
    template_name = "a4_candy_notifications/emails/notify_initiators_publish_results"

    def get_organisation(self):
        return self.object.organisation

    def get_receivers(self):
        receivers = self.object.organisation.initiators.all()
        return _exclude_notifications_disabled(
            receivers, "email_initiator_publish_results"
        )

    def get_context(self):
        context = super().get_context()
        project = self.object
        context["project"] = project
        context["result_edit_url"] = reverse(
            "a4dashboard:dashboard-result-edit",
            kwargs={
                "organisation_slug": project.organisation.slug,
                "project_slug": project.slug,
            },
        )
        return context
