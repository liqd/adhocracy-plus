from django.apps import AppConfig


class Config(AppConfig):
    name = 'liqd_product.apps.projects'
    label = 'liqd_product_projects'

    def ready(self):
        import liqd_product.apps.projects.signals # noqa
