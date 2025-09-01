from django import template
from apps.notifications.models import Notification

register = template.Library()

@register.simple_tag(takes_context=True)
def unread_notifications_count(context):
    request = context['request']
    if request.user.is_authenticated:
        return Notification.objects.unread_count_for_user(request.user)
    return 0