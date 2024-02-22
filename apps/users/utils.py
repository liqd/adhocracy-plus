from django.conf import settings
from django.utils import translation

from .models import User


def set_session_language(user_email, language=None, request=None):
    if not language:
        language = User.objects.get(email=user_email).language
    translation.activate(language)
    if hasattr(request, "COOKIES"):
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = language
