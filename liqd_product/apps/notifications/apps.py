from django.apps import AppConfig


class Config(AppConfig):
    name = 'liqd_product.apps.notifications'
    label = 'liqd_product_notifications'

    def ready(self):
        import liqd_product.apps.notifications.signals  # noqa:F401
