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
        res = []
        try:
            language = User.objects.get(email=receiver).language
            res = [language, self.fallback_language]
        except User.DoesNotExist:
            res = super().get_languages(receiver)
        return res
