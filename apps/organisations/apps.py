from django.apps import AppConfig


class Config(AppConfig):
    name = 'apps.organisations'
    label = 'a4_candy_organisations'

    def ready(self):
        from . import function_overwrites  # noqa
