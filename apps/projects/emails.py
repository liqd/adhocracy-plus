from apps.users.emails import EmailAplus as Email


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
