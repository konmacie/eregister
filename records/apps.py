from django.apps import AppConfig


class RecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'records'

    # Moved signals connections to .models.__init__.py
    # def ready(self):
    #     # generate random username for users without one
    #     pre_save.connect(generate_username, sender=settings.AUTH_USER_MODEL)
