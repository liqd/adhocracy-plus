from django.conf import settings
from django.utils import translation


class SetUserLanguageCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if hasattr(request.user, "language"):
            translation.activate(request.user.language)
            if cookie != request.user.language:
                response.set_cookie(
                    settings.LANGUAGE_COOKIE_NAME,
                    request.user.language,
                    max_age=settings.LANGUAGE_COOKIE_AGE,
                    path=settings.LANGUAGE_COOKIE_PATH,
                    domain=settings.LANGUAGE_COOKIE_DOMAIN,
                    secure=settings.LANGUAGE_COOKIE_SECURE,
                    httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                    samesite=settings.LANGUAGE_COOKIE_SAMESITE,
                )
        return response
