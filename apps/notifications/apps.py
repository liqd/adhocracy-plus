from django.apps import AppConfig


class Config(AppConfig):
    name = "apps.notifications"
    label = "a4_candy_notifications"

    def ready(self):
        from . import signals