from django.apps import AppConfig


class Config(AppConfig):
    name = "apps.contrib"
    label = "a4_candy_contrib"

    def ready(self):
        from apps.contrib.a4_emails import patch_report_moderator_email
        from apps.contrib.widgets import ImageInputWidget

        patch_report_moderator_email()

        from adhocracy4.images import forms as a4_image_forms

        a4_image_forms.ImageField.widget = ImageInputWidget
