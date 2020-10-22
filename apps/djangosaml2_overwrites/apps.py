from django.apps import AppConfig


class Config(AppConfig):
    name = 'apps.djangosaml2_overwrites'

    def ready(self):
        from . import overwrites
        overwrites.apply_custom_overwrites()
