from django.apps import AppConfig



class NypostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nypost'

    def ready(self):
        import nypost.signals
