from django.apps import AppConfig


class Config(AppConfig):
    name = "apps.users"
    label = "a4_candy_users"

    def ready(self):
        import apps.users.signals  # noqa
