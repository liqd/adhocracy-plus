from django import forms
from django.utils.translation import gettext_lazy as _

from .utils import verify_token
from .widgets import ProsopoCaptchaWidget


class ProsopoCaptchaField(forms.CharField):
    widget = ProsopoCaptchaWidget

    def validate(self, value):
        super().validate(value)

        if not value:
            raise forms.ValidationError(_("Please complete the captcha."))

        # Verify the token with Prosopo server
        if not verify_token(value):
            raise forms.ValidationError(
                _("Captcha verification failed. Please try again.")
            )
        return value
