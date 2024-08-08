from django.utils.translation import activate

from .models import User


def set_session_language(user_email, language=None):
    if not language:
        language = User.objects.get(email=user_email).language
    activate(language)
