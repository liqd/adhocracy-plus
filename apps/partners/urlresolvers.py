import itertools

from django.conf.urls import include
from django.conf.urls import url
from django.urls import URLPattern
from django.urls import URLResolver

from apps.django_overwrites.urlresolvers import django_reverse

from . import get_partner

_partner_pattern_names = set()


def partner_patterns(*pattern_list):
    """Mark the url patterns used with partners."""
    for pattern in pattern_list:
        if isinstance(pattern, URLPattern):
            _partner_pattern_names.add(pattern.name)
        elif isinstance(pattern, URLResolver):
            for url_pattern in pattern.url_patterns:
                ns = ''
                if pattern.app_name:
                    ns = ns + pattern.app_name + ':'
                elif pattern.namespace:
                    ns = ns + pattern.namespace + ':'
                _partner_pattern_names.add(ns + url_pattern.name)
        else:
            raise Exception()

    return url(r'^(?P<partner_slug>[-\w_]+)/',
               include(list(pattern_list)))


def reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None):
    """Add the current partner to the url if none is set yet."""
    if viewname in _partner_pattern_names and get_partner():
        partner_slug = get_partner().slug
        if args:
            # Attention: Assumes a manual partner_slug is always set as kwarg
            args = list(itertools.chain((partner_slug,), args))
        elif kwargs and 'partner_slug' not in kwargs:
            kwargs['partner_slug'] = partner_slug
        elif not kwargs:
            kwargs = {'partner_slug': partner_slug}

    return django_reverse(viewname, urlconf, args, kwargs, current_app)
