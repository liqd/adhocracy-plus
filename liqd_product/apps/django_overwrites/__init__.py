from . import urlresolvers

default_app_config = 'liqd_product.apps.django_overwrites.apps.Config'

urlresolvers.patch_reverse()
