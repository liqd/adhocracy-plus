from django.apps import AppConfig


class Config(AppConfig):
    name = 'apps.projects'
    label = 'a4_candy_projects'

    def ready(self):
        from . import overwrites
        from . import signals  # noqa
        overwrites.overwrite_access_enum_label()
