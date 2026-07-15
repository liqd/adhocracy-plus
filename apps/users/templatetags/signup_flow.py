from urllib.parse import quote
from urllib.parse import urlencode

from django import template
from django.urls import reverse

from apps.users.constants import GUEST_SWITCH_QUERY_PARAM

from .userindicator import get_next_url

register = template.Library()


def _url_with_next(url_name, request):
    return f"{reverse(url_name)}?{urlencode({'next': get_next_url(request)})}"


@register.simple_tag(takes_context=True)
def guest_url(context):
    request = context.get("request")
    if not request:
        return ""

    next_param = get_next_url(request)
    encoded_next_param = quote(next_param)
    guest_create_url = reverse("guest_create")

    return f"{guest_create_url}?next={encoded_next_param}"


@register.simple_tag(takes_context=True)
def guest_convert_url(context):
    request = context.get("request")
    if not request:
        return ""
    return _url_with_next("guest_convert", request)


@register.simple_tag(takes_context=True)
def guest_personal_login_url(context):
    """Return logout URL that sends guests to login with a return path."""
    request = context.get("request")
    if not request:
        return ""
    login_url = _url_with_next("account_login", request)
    query = urlencode({"next": login_url})
    return f"{reverse('account_logout')}?{GUEST_SWITCH_QUERY_PARAM}=1&{query}"
