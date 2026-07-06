from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from apps.captcha.utils import verify_token


def prosopo_captcha_backend(request, poll):
    if not getattr(settings, "CAPTCHA", False):
        return

    token = request.data.get("captcha", "")
    if not token:
        raise ValidationError(_("Please complete the captcha."))

    if not verify_token(token):
        raise ValidationError(_("Captcha verification failed. Please try again."))


def poll_extra_attributes(poll):
    return {
        "prosopoSiteKey": getattr(settings, "PROSOPO_SITE_KEY", ""),
        "captchaEnabled": bool(getattr(settings, "CAPTCHA", False)),
        "captchaType": "prosopo",
    }
