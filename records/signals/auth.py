from django.utils.text import slugify
import uuid


def generate_username(sender, instance, **kwargs):
    """
    Generate random username based on first_name and uuid4.
    Generated form: {slugified user.first_name}.{random uuid4[:8]}
    """
    if not instance.username:
        instance.username = "{}.{}".format(
            slugify(instance.first_name),
            uuid.uuid4().hex[:8]
        )
