from django.utils.translation import ugettext_lazy as _

from adhocracy4.filters import filters as a4_filters
from adhocracy4.filters import widgets as filters_widgets
from adhocracy4.filters.filters import FreeTextFilter
from apps.contrib import filters

from . import models


class FreeTextFilterWidget(filters_widgets.FreeTextFilterWidget):
    label = _('Search')


class SubjectFilterSet(a4_filters.DefaultsFilterSet):
    defaults = {
        'ordering': 'name'
    }

    ordering = filters.OrderingFilter(
        choices=(
            ('name', _('Alphabetical')),
            ('-comment_count', _('Most commented'))
        )
    )
    search = FreeTextFilter(
        widget=FreeTextFilterWidget,
        fields=['name']
    )

    class Meta:
        model = models.Subject
        fields = ['search']


class SubjectCreateFilterSet(a4_filters.DefaultsFilterSet):

    defaults = {
        'ordering': 'name'
    }

    ordering = filters.OrderingFilter(
        choices=(
            ('name', _('Alphabetical')),
        )
    )

    class Meta:
        model = models.Subject
        fields = []
