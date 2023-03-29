from django.apps import AppConfig
from journal.nypost import signals


class NypostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nypost'

    def ready(self):
        import journal.nypost.signals
