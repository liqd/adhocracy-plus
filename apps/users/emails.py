from adhocracy4.emails import Email

from .models import User


class EmailWithUserLanguage(Email):

    def get_languages(self, receiver):
        res = []
        try:
            language = User.objects.get(email=receiver).language
            res = [language, self.fallback_language]
        except User.DoesNotExist:
            res = super(EmailWithUserLanguage, self).get_languages(receiver)
        return res
