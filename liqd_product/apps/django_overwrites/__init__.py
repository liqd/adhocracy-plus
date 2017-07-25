initialized = False

if not initialized:
    initialized = True

    from django.conf import settings
    from . import urlresolvers

    if hasattr(settings, 'REVERSE_METHOD'):
        urlresolvers.patch_reverse()
