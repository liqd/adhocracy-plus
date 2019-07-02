from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation import activate

from .models import User


def set_session_language(user_email, language=None, request=None):
    if not language:
        language = User.objects.get(email=user_email).language
    activate(language)
    if hasattr(request, 'session'):
        request.session[LANGUAGE_SESSION_KEY] = language
