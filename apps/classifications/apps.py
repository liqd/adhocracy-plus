from django.apps import AppConfig


class Config(AppConfig):
    name = 'apps.classifications'
    label = 'a4_candy_classifications'

    def ready(self):
        import apps.classifications.signals  # noqa:F401
