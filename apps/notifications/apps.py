from django.apps import AppConfig


class Config(AppConfig):
    name = 'apps.notifications'
    label = 'liqd_product_notifications'

    def ready(self):
        import apps.notifications.signals  # noqa:F401
