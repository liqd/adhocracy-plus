from django.contrib.auth import get_user_model

from apps.users.emails import EmailAplus as Email

User = get_user_model()


class InviteParticipantEmail(Email):
    template_name = 'a4_candy_projects/emails/invite_participant'

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        return [self.object.email]


class InviteModeratorEmail(Email):
    template_name = 'a4_candy_projects/emails/invite_moderator'

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        return [self.object.email]


class WelcomeToPrivateProjectEmail(Email):
    template_name = 'a4_candy_projects/emails/welcome_participant'

    def get_organisation(self):
        return self.object.organisation

    def get_receivers(self):
        participant_pks = self.kwargs['participant_pks']
        receivers = User.objects.filter(pk__in=participant_pks)
        return receivers
