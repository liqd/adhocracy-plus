from django.template import defaultfilters
from django.utils import timezone


def get_date_display(date):
    local_date = timezone.localtime(date)
    return "{}, {}".format(
        defaultfilters.date(local_date), defaultfilters.time(local_date)
    )
