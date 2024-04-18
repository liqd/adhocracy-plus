from django.contrib.auth.signals import user_logged_in
from django.utils.translation import gettext_lazy as _

USERNAME_REGEX = r"^[\w]+[ \w.@+-]*$"
USERNAME_INVALID_MESSAGE = _(
    "Enter a valid username. This value may contain "
    "only letters, digits, spaces and @/./+/-/_ "
    "characters. It must start with a digit or a "
    "letter."
)


def set_language(sender, user, **kwargs):
    from .utils import set_session_language

    set_session_language(user.email)


user_logged_in.connect(set_language)
