import json

from django import template
from django.conf import settings
from django.utils.html import format_html

from adhocracy4.polls.models import Poll

register = template.Library()


@register.simple_tag
def react_polls_prosopo(poll: Poll):
    attributes = {
        "pollId": poll.pk,
        "enableUnregisteredUsers": getattr(
            settings, "A4_POLL_ENABLE_UNREGISTERED_USERS", False
        ),
        "prosopoSiteKey": getattr(settings, "PROSOPO_SITE_KEY", ""),
        "captchaEnabled": bool(getattr(settings, "CAPTCHA", False)),
    }

    return format_html(
        '<div data-a4-widget="polls" data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes),
    )
