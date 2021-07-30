from django.apps import AppConfig
from django.db.models.signals import post_migrate
from records.signals.auth import create_default_user_groups


class RecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'records'

    def ready(self):
        # Moved signal connection to .models.__init__.py
        # # generate random username for users without one
        # pre_save.connect(generate_username, sender=settings.AUTH_USER_MODEL)

        # generate default permissions groups post migrate
        post_migrate.connect(create_default_user_groups, sender=self)
