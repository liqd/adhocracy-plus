from apps.organisations.models import Organisation
from apps.projects import tasks
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
            'organisation_id': organisation.id
        }
        tasks.send_async_no_object(
            cls.__module__, cls.__name__,
            object_dict, args, kwargs)
        return []

    def get_organisation(self):
        return Organisation.objects.get(id=self.object['organisation_id'])

    def get_receivers(self):
        return self.object['initiators']

    def get_context(self):
        context = super().get_context()
        context['name'] = self.object['name']
        return context
