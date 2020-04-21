from email.mime.image import MIMEImage

from django.conf import settings

from adhocracy4.emails import Email

from .models import User


class EmailAplus(Email):

    def get_organisation(self):
        return

    def get_site(self):
        organisation = self.get_organisation()
        if organisation is not None:
            site = organisation.site
            if site is not None:
                return site
        return super().get_site()

    def get_languages(self, receiver):
        languages = super().get_languages(receiver)

        if hasattr(settings, 'DEFAULT_USER_LANGUAGE_CODE'):
            languages.insert(0, settings.DEFAULT_USER_LANGUAGE_CODE)

        if User.objects.filter(email=receiver).exists():
            languages.insert(0, User.objects.get(email=receiver).language)

        return languages

    def get_context(self):
        context = super().get_context()
        context['organisation'] = self.get_organisation()
        return context

    def get_attachments(self):
        attachments = super().get_attachments()

        organisation = self.get_organisation()
        if organisation and organisation.logo:
            f = open(organisation.logo.path, 'rb')
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<{}>'.format('organisation_logo'))
            attachments += [logo]
            # need to remove standard email logo bc some email clients
            # display all attachments, even if not used
            attachments = [a for a in attachments
                           if a['Content-Id'] != '<logo>']

        return attachments
