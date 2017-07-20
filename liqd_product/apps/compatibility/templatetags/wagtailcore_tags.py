from django import template
from django.utils.safestring import mark_safe

from .. import warn_compatibilty_layer

register = template.Library()


@register.filter
def richtext(value):
    warn_compatibilty_layer()
    return mark_safe('<div class="rich-text">' + value + '</div>')
