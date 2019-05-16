import contextlib
import threading

default_app_config = 'apps.partners.apps.Config'

_partner = threading.local()


def set_partner(partner):
    _partner.value = partner


def get_partner():
    return getattr(_partner, 'value', None)


@contextlib.contextmanager
def partner_context(partner):
    prev_partner = get_partner()

    set_partner(partner)
    try:
        yield
    finally:
        if prev_partner:
            set_partner(prev_partner)
        else:
            clear_partner()


def clear_partner():
    try:
        del _partner.value
    except AttributeError:
        pass
