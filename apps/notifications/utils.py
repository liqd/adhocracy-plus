from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .constants import NOTIFICATION_SECTIONS


def format_event_date(event_date):
    """
    Format event date as DD.MM.YYYY
    """
    if not event_date:
        return _("soon")

    # Convert to local timezone if it has time
    if event_date.time() != timezone.datetime.min.time():
        event_date = timezone.localtime(event_date)

    # Always return DD.MM.YYYY
    return event_date.strftime("%d.%m.%Y")


def get_notifications_by_section(notifications, section):
    """
    Filter notifications by section

    Args:
        notifications: Notification queryset
        section: Section name from NOTIFICATION_SECTIONS

    Returns:
        Filtered notification queryset
    """
    if section not in NOTIFICATION_SECTIONS:
        return notifications.none()

    section_types = NOTIFICATION_SECTIONS[section]
    q_objects = Q()
    for notification_type in section_types:
        q_objects |= Q(notification_type=notification_type)

    return notifications.filter(q_objects)
