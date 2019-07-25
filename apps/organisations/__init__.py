import contextlib
import threading

default_app_config = 'apps.organisations.apps.Config'

_organisation = threading.local()


def set_organisation(organisation):
    _organisation.value = organisation


def get_organisation():
    return getattr(_organisation, 'value', None)


@contextlib.contextmanager
def organisation_context(organisation):
    prev_organisation = get_organisation()

    set_organisation(organisation)
    try:
        yield
    finally:
        if prev_organisation:
            set_organisation(prev_organisation)
        else:
            clear_organisation()


def clear_organisation():
    try:
        del _organisation.value
    except AttributeError:
        pass
