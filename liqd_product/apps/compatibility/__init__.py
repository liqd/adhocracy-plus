import warnings

from django.utils.deprecation import RemovedInNextVersionWarning


class CompatibilityLayerWarning(DeprecationWarning):
    pass


def warn_compatibilty_layer():
    # FIXME: Using the RemovedInNextVersionWarning to show warnings in dev
    # server. Could probably fixed to show also CompatibilityLayerWarnings
    warnings.warn('compatibility layer should be removed',
                  RemovedInNextVersionWarning, stacklevel=2)
