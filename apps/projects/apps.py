from django.apps import AppConfig


class Config(AppConfig):
    name = 'apps.projects'
    label = 'liqd_product_projects'

    def ready(self):
        import apps.projects.signals # noqa
