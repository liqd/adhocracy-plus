from allauth.account.models import EmailAddress
from django.shortcuts import redirect
from django.urls import reverse


class SamlSignupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            email = EmailAddress.objects.get(user=request.user,
                                             email=request.user.email)
            if not email.verified:
                path = request.path
                view = request.resolver_match.view_name

                allowed_paths = [
                    reverse('saml2_signup'),
                    reverse('saml2_logout'),
                    reverse('set_language'),
                    reverse('javascript-catalog')
                ]
                allowed_views = [
                    'wagtail_serve'
                ]

                if path not in allowed_paths and view not in allowed_views:
                    return redirect(reverse('saml2_signup') + "?next=" + path)
