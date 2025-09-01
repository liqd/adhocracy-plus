from django import template
from apps.notifications.models import Notification
from django.utils.safestring import mark_safe
register = template.Library()

@register.simple_tag(takes_context=True)
def unread_notifications_count(context):
    request = context['request']
    if request.user.is_authenticated:
        return Notification.objects.unread_count_for_user(request.user)
    return 0

@register.filter
def render_notification_with_links(notification):
    context = notification.context
    template_parts = notification.message_template.split('{')
    
    result = []
    for part in template_parts:
        if '}' in part:
            key, rest = part.split('}', 1)
            if key in context:
                if f"{key}_url" in context:
                    result.append(f'<a href="{context[f"{key}_url"]}">{context[key]}</a>')
                else:
                    result.append(context[key])
            result.append(rest)
        else:
            result.append(part)
    
    return mark_safe(''.join(result))
