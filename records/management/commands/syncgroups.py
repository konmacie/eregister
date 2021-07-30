from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission, Group
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        for group_name, perms_codenames in settings.DEFAULT_GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write('"%s" group created.' % group)
            perms = Permission.objects.filter(
                codename__in=perms_codenames
            )
            group.permissions.set(perms)
            self.stdout.write('Permissions for "%s" set.' % group)
