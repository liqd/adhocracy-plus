from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag(takes_context=True)
def get_absolute_uri(context, obj):
    return context['request'].build_absolute_uri(obj)


@register.simple_tag(takes_context=True)
def get_absolute_uri_static(context, obj):
    return context['request'].build_absolute_uri(static(obj))
