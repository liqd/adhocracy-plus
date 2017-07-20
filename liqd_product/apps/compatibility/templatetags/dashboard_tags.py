from django import template

from .. import warn_compatibilty_layer

register = template.Library()


@register.filter
def get_blueprint_title(key):
    warn_compatibilty_layer()
    return key
