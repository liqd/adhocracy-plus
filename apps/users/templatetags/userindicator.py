from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse

from allauth.account import urls as account_urls
from django import template
from django.urls import Resolver404
from django.urls import resolve

INVALID_URL_NAME = object()

register = template.Library()


def _is_account_url(request):
    try:
        url_name = resolve(request.path).url_name
    except Resolver404:
        return False

    return (
        any(url_name == url.name for url in account_urls.urlpatterns)
        or url_name == "guest_create"
    )


def get_next_url(request):
    """
    Returns the correct "next" URL, ensuring it doesn't already contain a "next" parameter.
    """
    if _is_account_url(request):
        next_param = request.GET.get("next") or request.POST.get("next") or "/"
    else:
        # Get the full path and parse it
        full_path = request.get_full_path()
        parsed_url = urlparse(full_path)

        # Parse the query parameters
        query_params = parse_qs(parsed_url.query)

        # Remove the "next" parameter if it exists
        if "next" in query_params:
            del query_params["next"]

        # Rebuild the URL without the "next" parameter
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse(parsed_url._replace(query=new_query))

        next_param = new_url

    # Decode the next parameter to ensure consistency
    return unquote(next_param)


@register.inclusion_tag("a4_candy_users/indicator.html", takes_context=True)
def userindicator(context):
    if hasattr(context, "request"):
        next_param = get_next_url(context["request"])
        encoded_next_param = quote(next_param)  # Encode the next parameter
        context["redirect_field_value"] = encoded_next_param
    return context
