
from django.conf import settings
from django.utils.text import slugify
import uuid
import logging

logger = logging.getLogger(__name__)


def generate_username(sender, instance, **kwargs):
    """
    Generate random username based on first_name and uuid4.
    Generated username: {slugified user.first_name}.{random uuid4[:8]}
    """
    if not instance.username:
        instance.username = "{}.{}".format(
            slugify(instance.first_name),
            uuid.uuid4().hex[:8]
        )


def create_default_user_groups(sender, **kwargs):
    """
    Called by post_migrate signal.
    Create default user groups for teachers and educators,
    and assign permissions selected in settings_local.py.
    """
    from django.contrib.auth.models import Permission, Group
    for group_name, perms_codenames in settings.DEFAULT_GROUPS.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            perms = Permission.objects.filter(
                codename__in=perms_codenames
            )
            group.permissions.set(perms)
            logger.info("Created default group %s\nPermissions:" % group_name)
            logger.info(perms_codenames)
        else:
            logger.warning("Group %s already exists. Skipping." % group_name)
