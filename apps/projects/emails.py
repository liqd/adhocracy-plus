from email.mime.image import MIMEImage

from apps.projects import tasks
from apps.users.emails import EmailWithUserLanguage as Email


class InviteParticipantEmail(Email):
    template_name = 'a4_candy_projects/emails/invite_participant'

    def get_receivers(self):
        return [self.object.email]

    def get_attachments(self):
        attachments = super().get_attachments()

        organisation = self.object.project.organisation
        if organisation and organisation.logo:
            f = open(organisation.logo.path, 'rb')
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<{}>'.format('organisation_logo'))
            attachments += [logo]

        return attachments

    def get_context(self):
        context = super().get_context()
        context['organisation'] = self.object.project.organisation
        return context


class InviteModeratorEmail(Email):
    template_name = 'a4_candy_projects/emails/invite_moderator'

    def get_receivers(self):
        return [self.object.email]

    def get_attachments(self):
        attachments = super().get_attachments()

        organisation = self.object.project.organisation
        if organisation and organisation.logo:
            f = open(organisation.logo.path, 'rb')
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<{}>'.format('organisation_logo'))
            attachments += [logo]

        return attachments

    def get_context(self):
        context = super().get_context()
        context['organisation'] = self.object.project.organisation
        return context


class DeleteProjectEmail(Email):
    template_name = 'a4_candy_projects/emails/delete_project'

    @classmethod
    def send_no_object(cls, object, *args, **kwargs):
        organisation = object.organisation
        object_dict = {
            'name': object.name,
            'initiators': list(organisation.initiators.all()
                               .distinct()
                               .values_list('email', flat=True)),
            'organisation': organisation.name
        }
        tasks.send_async_no_object(
            cls.__module__, cls.__name__,
            object_dict, args, kwargs)
        return []

    def get_receivers(self):
        return self.object['initiators']

    def get_context(self):
        context = super().get_context()
        context['name'] = self.object['name']
        context['organisation'] = self.object['organisation']
        return context
