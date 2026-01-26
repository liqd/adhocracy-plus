from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from apps.notifications.models import Notification

register = template.Library()


@register.simple_tag(takes_context=True)
def unread_notifications_count(context):
    request = context["request"]
    if request.user.is_authenticated:
        return Notification.objects.unread_count_for_user(request.user)
    return 0


@register.filter
def render_notification_with_links(notification):
    message_template = _(notification.message_key)  # Translate at render time
    context = notification.context

    template_parts = message_template.split("{")

    result = []
    for part in template_parts:
        if "}" in part:
            key, rest = part.split("}", 1)
            if key in context:
                if f"{key}_url" in context:
                    mark_read_url = reverse(
                        "mark_notification_as_read", args=[notification.id]
                    )
                    redirect_url = context[f"{key}_url"]
                    result.append(
                        f'<a href="{mark_read_url}?redirect_to={redirect_url}">{context[key]}</a>'
                    )
                else:
                    result.append(context[key])
            result.append(rest)
        else:
            result.append(part)

    return mark_safe("".join(result))
