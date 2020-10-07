from email.mime.image import MIMEImage

from django.conf import settings
from django.template.loader import get_template
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from adhocracy4.emails import Email

from .models import User

ACCOUNT_LINK_TEXT = _('If you no longer want to receive any notifications, '
                      'change the settings for your {}account{}.')
PROJECT_LINK_TEXT = _('If you no longer want to receive notifications about '
                      'this project, unsubscribe from the {}project{}.')


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
        organisation = self.get_organisation()
        if User.objects.filter(email=receiver).exists():
            languages.insert(0, User.objects.get(email=receiver).language)
        elif organisation is not None:
            languages.insert(0, organisation.language)
        elif hasattr(settings, 'DEFAULT_USER_LANGUAGE_CODE'):
            languages.insert(0, settings.DEFAULT_USER_LANGUAGE_CODE)

        return languages

    def get_receiver_language(self, receiver):
        return self.get_languages(receiver)[0]

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

    def render(self, template_name, context):
        template = get_template(template_name + '.en.email')
        language = self.get_receiver_language(context['receiver'])
        with translation.override(language):
            context['account_link'] = \
                self.get_html_link(ACCOUNT_LINK_TEXT, reverse('account'))
            if 'action' in context:
                project = context['action'].project
                if project:
                    context['project_link'] = \
                        self.get_html_link(PROJECT_LINK_TEXT,
                                           project.get_absolute_url())

            parts = []
            for part_type in ('subject', 'txt', 'html'):
                context['part_type'] = part_type
                parts.append(template.render(context))
                context.pop('part_type')
        return tuple(parts)

    def get_html_link(self, link_text, url):

        link = link_text.format('<a href="' + self.get_host() + url
                                + '" target="_blank">', '</a>')
        return link
