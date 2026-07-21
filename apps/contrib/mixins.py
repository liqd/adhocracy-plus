from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.translation import gettext_lazy as _
from guest_user.functions import is_guest_user


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict view access to active Django staff users."""

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


RIGHT_OF_USE_LABEL = _(
    "I hereby confirm that the copyrights for this "
    "photo are with me or that I have received "
    "rights of use from the author. I also confirm "
    "that the privacy rights of depicted third persons "
    "are not violated. "
)


class GuestCreatorContactFieldMixin:
    """Keep creator contact email empty for guest users on create forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.user and is_guest_user(self.user):
            self.fields["creator_email"].initial = ""


class ImageRightOfUseMixin(forms.ModelForm):
    right_of_use = forms.BooleanField(required=False, label=RIGHT_OF_USE_LABEL)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.image:
            self.initial["right_of_use"] = True

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        right_of_use = cleaned_data.get("right_of_use")
        if image and not right_of_use:
            self.add_error(
                "right_of_use",
                _(
                    "You want to upload an image. "
                    "Please check that you have the "
                    "right of use for the image."
                ),
            )
        return cleaned_data
