from django.apps import AppConfig
from django.db.models.signals import pre_save
from records.signals.auth import generate_username


class RecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'records'

    def ready(self):
        # generate random username for users without one
        pre_save.connect(generate_username, sender='records.User')
