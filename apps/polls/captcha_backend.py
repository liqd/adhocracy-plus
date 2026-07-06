from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from wagtail.models import Site

from apps.captcha.utils import verify_token
from apps.cms.settings.models import ImportantPages


def prosopo_captcha_backend(request, poll):
    if not getattr(settings, "CAPTCHA", False):
        return

    token = request.data.get("captcha", "")
    if not token:
        raise ValidationError(_("Please complete the captcha."))

    if not verify_token(token):
        raise ValidationError(_("Captcha verification failed. Please try again."))


def poll_extra_attributes(poll):
    site = Site.objects.filter(is_default_site=True).first()
    important_pages = ImportantPages.for_site(site) if site else None
    manual_link = important_pages.manual_link if important_pages else ""

    return {
        "prosopoSiteKey": getattr(settings, "PROSOPO_SITE_KEY", ""),
        "captchaEnabled": bool(getattr(settings, "CAPTCHA", False)),
        "captchaType": "prosopo",
        "manualLink": manual_link,
    }
