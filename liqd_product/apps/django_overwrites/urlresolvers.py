import importlib

from django import urls
from django.conf import settings
from django.utils import six
from django.utils.functional import lazy

django_reverse = None
django_reverse_lazy = None


def patch_reverse():
    """Overwrite the default reverse implementation.

    Monkey-patches the urlresolvers.reverse function. Will not patch twice.
    """
    global django_reverse, django_reverse_lazy
    if hasattr(settings, 'REVERSE_METHOD') and django_reverse is None:
        django_reverse = urls.reverse
        django_reverse_lazy = urls.reverse_lazy

        module_name, func_name = settings.REVERSE_METHOD.rsplit('.', 1)
        reverse = getattr(importlib.import_module(module_name), func_name)

        urls.reverse = reverse
        urls.reverse_lazy = lazy(reverse, six.text_type)


def reset_reverse():
    """Restore the default reverse implementation."""
    if django_reverse is not None:
        urls.reverse = django_reverse
        urls.reverse_lazy = django_reverse_lazy
