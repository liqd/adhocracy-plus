from django.apps import AppConfig


class Config(AppConfig):
    name = "apps.contrib"
    label = "a4_candy_contrib"

    def ready(self):
        from apps.contrib.a4_emails import patch_report_moderator_email

        patch_report_moderator_email()
