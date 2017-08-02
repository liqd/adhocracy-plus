from django import template
from django.contrib.staticfiles.finders import find
from django.templatetags.static import static

INVALID_URL_NAME = object()

register = template.Library()


@register.simple_tag(takes_context=True)
def static_css(context):
    partner = context['request'].partner
    filename = 'adhocracy4.css'

    if partner:
        _filename = 'styles_{slug}.css'.format(slug=partner.slug)
        # check if file actually exists before assigning
        if find(_filename):
            filename = _filename

    return static(filename)
