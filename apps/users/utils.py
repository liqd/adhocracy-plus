import random
import re

from django.conf import settings
from django.utils.translation import activate
from django.utils.translation import get_language

from .guest_username_words import GUEST_USERNAME_ADJECTIVES_DE
from .guest_username_words import GUEST_USERNAME_ADJECTIVES_EN
from .guest_username_words import GUEST_USERNAME_NOUNS_DE
from .guest_username_words import GUEST_USERNAME_NOUNS_EN
from .models import User


def set_session_language(user_email, language=None):
    if not language:
        language = User.objects.get(email=user_email).language
    activate(language)


GUEST_USERNAME_WORDS = {
    "de": (GUEST_USERNAME_ADJECTIVES_DE, GUEST_USERNAME_NOUNS_DE),
    "en": (GUEST_USERNAME_ADJECTIVES_EN, GUEST_USERNAME_NOUNS_EN),
}


def _guest_username_words():
    """Return the adjective/noun lists for the currently active language."""
    language = get_language() or settings.LANGUAGE_CODE
    return GUEST_USERNAME_WORDS.get(language.split("-")[0], GUEST_USERNAME_WORDS["en"])


def generate_guest_username():
    """Return a unique and friendly username for a guest account.

    A readable "Adjective Noun" combination is preferred. If free names run
    low, a number is appended so the number of possible guest names stays
    effectively unlimited.
    """
    adjectives, nouns = _guest_username_words()

    for _ in range(50):
        username = "{} {}".format(random.choice(adjectives), random.choice(nouns))
        if not User.objects.filter(username__iexact=username).exists():
            return username

    while True:
        username = "{} {} {}".format(
            random.choice(adjectives),
            random.choice(nouns),
            random.randint(1, 9999),
        )
        if not User.objects.filter(username__iexact=username).exists():
            return username


# Characters that are not allowed in an email local part and are therefore
# replaced when deriving the guest placeholder email from the username.
_GUEST_EMAIL_UNSAFE = re.compile(r"[^A-Za-z0-9._+-]")
_GUEST_EMAIL_TRANSLITERATION = str.maketrans(
    {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}
)


def guest_email_for_username(username):
    """Return a unique placeholder email used for a guest account.

    django-guest-user derives ``guest+<username>@liqd.net`` from the username,
    but usernames may contain characters that are not valid in an email address
    (e.g. the German gender colon, spaces or "@"). Those are transliterated or
    replaced with an underscore. As this mapping is many-to-one, a numeric
    suffix keeps the placeholder email unique: ``User.email`` is used as a
    login key and must not be ambiguous.
    """
    local_part = username.translate(_GUEST_EMAIL_TRANSLITERATION)
    local_part = _GUEST_EMAIL_UNSAFE.sub("_", local_part)
    email = "guest+{}@liqd.net".format(local_part)
    suffix = 1
    while User.objects.filter(email=email).exists():
        email = "guest+{}{}@liqd.net".format(local_part, suffix)
        suffix += 1
    return email
