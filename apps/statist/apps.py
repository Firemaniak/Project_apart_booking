from django.apps import AppConfig


class StatistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.statist'
    label = 'statist'

    def ready(self):
        import apps.statist.signals  # noqa