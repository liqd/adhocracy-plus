from django.apps import AppConfig


class Config(AppConfig):
    name = 'apps.projects'
    label = 'a4_candy_projects'

    def ready(self):
        import apps.projects.signals # noqa
