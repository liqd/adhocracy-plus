from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from adhocracy4.polls.api import PollViewSet as BasePollViewSet
from apps.captcha.utils import verify_token


class PollViewSet(BasePollViewSet):
    def check_captcha(self):
        # Wenn CAPTCHA global deaktiviert ist, keine Prüfung erzwingen.
        if not getattr(settings, "CAPTCHA", False):
            return

        token = self.request.data.get("captcha", "")
        if not token:
            raise ValidationError(_("Please complete the captcha."))

        # Prosopo-Token direkt prüfen (kein Legacy-Captcheck mehr).
        if not verify_token(token):
            raise ValidationError(_("Captcha verification failed. Please try again."))
