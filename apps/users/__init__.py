from django.contrib.auth.signals import user_logged_in
from django.utils.translation import ugettext_lazy as _

default_app_config = 'apps.users.apps.Config'

USERNAME_REGEX = r'^[\w]+[ \w.@+-]*$'
USERNAME_INVALID_MESSAGE = _('Enter a valid username. This value may contain '
                             'only letters, digits, spaces and @/./+/-/_ '
                             'characters. It must start with a digit or a '
                             'letter.')


def set_language(sender, user, request, **kwargs):
    from .utils import set_session_language
    set_session_language(user, None, request)


user_logged_in.connect(set_language)
