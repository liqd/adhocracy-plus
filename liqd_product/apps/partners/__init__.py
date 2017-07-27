import threading

_partner = threading.local()


def set_partner(partner):
    _partner.value = partner


def get_partner():
    return getattr(_partner, 'value', None)


def clear_partner():
    try:
        del _partner.value
    except AttributeError:
        pass
