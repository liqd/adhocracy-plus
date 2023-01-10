from django.utils.translation import gettext_lazy as _

from adhocracy4.filters import filters as a4_filters
from adhocracy4.filters import widgets as filters_widgets
from adhocracy4.filters.filters import FreeTextFilter
from apps.contrib.widgets import AplusOrderingWidget

from . import models


class FreeTextFilterWidget(filters_widgets.FreeTextFilterWidget):
    label = _("Search")


class SubjectFilterSet(a4_filters.DefaultsFilterSet):
    defaults = {"ordering": "name"}

    ordering = a4_filters.DynamicChoicesOrderingFilter(
        choices=(("name", _("Alphabetical")), ("-comment_count", _("Most commented"))),
        widget=AplusOrderingWidget,
    )
    search = FreeTextFilter(widget=FreeTextFilterWidget, fields=["name"])

    class Meta:
        model = models.Subject
        fields = ["search"]


class SubjectCreateFilterSet(a4_filters.DefaultsFilterSet):

    defaults = {"ordering": "name"}

    ordering = a4_filters.DynamicChoicesOrderingFilter(
        choices=(("name", _("Alphabetical")),), widget=AplusOrderingWidget
    )

    class Meta:
        model = models.Subject
        fields = []
