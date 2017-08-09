import contextlib
import threading

_partner = threading.local()


def set_partner(partner):
    _partner.stack = [partner]


def get_partner():
    if hasattr(_partner, 'stack'):
        return _partner.stack[-1]


@contextlib.contextmanager
def partner_context(partner):
    if not hasattr(_partner, 'stack'):
        _partner.stack = []

    _partner.stack.append(partner)
    try:
        yield
    finally:
        _partner.stack.pop()
        if not _partner.stack:
            del _partner.stack


def clear_partner():
    try:
        del _partner.stack
    except AttributeError:
        pass
