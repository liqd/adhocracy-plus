from django import forms

from .models import NotificationSettings


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        fields = [
            # Project related
            "email_newsletter",
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
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs.update({"class": "form-check-input"})
