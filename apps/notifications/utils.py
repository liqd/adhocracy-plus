from django.db.models import Q
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from .constants import NOTIFICATION_SECTIONS


def format_event_date(event_date):
    """
    Format event date for notifications with timezone awareness

    Args:
        event_date: DateTime object

    Returns:
        Formatted date string or "soon" if no date
    """
    if not event_date:
        return _("soon")

    if event_date.time() == timezone.datetime.min.time():
        # Date only (no specific time)
        return date_format(event_date, "DATE_FORMAT")
    else:
        # Date with time - convert to local timezone
        return date_format(timezone.localtime(event_date), "DATETIME_FORMAT")


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
