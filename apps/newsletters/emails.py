from django.apps import apps
from django.conf import settings
from django.contrib import auth

from adhocracy4.emails.mixins import ReportToAdminEmailMixin
from apps.users.emails import EmailAplus as Email

Organisation = apps.get_model(settings.A4_ORGANISATIONS_MODEL)
User = auth.get_user_model()


class NewsletterEmail(ReportToAdminEmailMixin, Email):
    template_name = 'a4_candy_newsletters/emails/newsletter_email'

    def dispatch(self, object, *args, **kwargs):
        organisation_pk = kwargs.pop('organisation_pk', None)
        organisation = None
        if organisation_pk:
            organisation = Organisation.objects.get(pk=organisation_pk)
        kwargs['organisation'] = organisation

        return super().dispatch(object, *args, **kwargs)

    def get_reply_to(self):
        return ['{} <{}>'.format(self.object.sender_name, self.object.sender)]

    def get_organisation(self):
        return self.kwargs['organisation']

    def get_receivers(self):
        return User.objects\
            .filter(id__in=self.kwargs['participant_ids'])\
            .filter(get_newsletters=True)\
            .filter(is_active=True)\
            .distinct()


class NewsletterEmailAll(NewsletterEmail):

    def get_receivers(self):
        return User.objects\
            .filter(is_active=True)\
            .distinct()
