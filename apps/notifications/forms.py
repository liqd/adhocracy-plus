from django import forms
from django.utils.translation import gettext_lazy as _

from .models import NotificationSettings


class NotificationSettingsForm(forms.ModelForm):
    # Newsletter opt-in lives on the User model (User.get_newsletters) and is
    # read by the newsletter sender. It must NOT default to True: this field
    # only reflects and changes the user's explicit choice.
    get_newsletters = forms.BooleanField(
        label=_("Email Newsletter"),
        required=False,
    )

    class Meta:
        model = NotificationSettings
        fields = [
            # Project related
            "email_initiator_publish_results",
            "email_project_updates",
            "notify_project_updates",
            "email_project_events",
            "notify_project_events",
            # User interactions
            "email_user_engagement",
            "notify_user_engagement",
            "email_messages",
            "notify_messages",
            "email_invitations",
            "notify_invitations",
            # Moderation
            "email_moderation",
            "notify_moderation",
            "email_warnings",
            "notify_warnings",
            # Tracking
            "track_project_updates",
            "track_project_events",
            "track_user_engagement",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["get_newsletters"].initial = self.instance.user.get_newsletters
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs.update({"class": "form-check-input"})

    def save(self, commit=True):
        user = self.instance.user
        user.get_newsletters = self.cleaned_data["get_newsletters"]
        user.save()
        return super().save(commit)
