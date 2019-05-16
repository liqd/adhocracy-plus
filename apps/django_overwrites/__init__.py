from . import urlresolvers

default_app_config = 'apps.django_overwrites.apps.Config'

urlresolvers.patch_reverse()
