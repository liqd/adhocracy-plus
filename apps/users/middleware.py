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
                    settings.LANGUAGE_COOKIE_NAME, request.user.language
                )
        return response
