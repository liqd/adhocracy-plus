from urllib.parse import quote

from django import template
from django.urls import reverse

from .userindicator import get_next_url

register = template.Library()


@register.simple_tag(takes_context=True)
def guest_url(context):
    request = context.get("request")
    if not request:
        return ""

    next_param = get_next_url(request)
    encoded_next_param = quote(next_param)
    guest_create_url = reverse("guest_create")

    return f"{guest_create_url}?next={encoded_next_param}"
