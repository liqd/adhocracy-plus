from django import template
from django.http import Http404
from django.urls import resolve
from django.urls import reverse
from django.utils import translation

register = template.Library()


@register.simple_tag(takes_context=True)
def translate_url(context, lang=None, *args, **kwargs):
    """
    Get active page's url by a specified language.

    Usage: {% translate_url 'en' %}
    """
    path = context['request'].path
    cur_language = translation.get_language()

    try:
        view = resolve(path)
        translation.activate(lang)
        url = reverse(
            view.view_name,
            args=view.args,
            kwargs=view.kwargs,
        )
    except Http404:
        url = '/' + lang + '/'
    finally:
        translation.activate(cur_language)
    return url
