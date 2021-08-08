from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    name = models.CharField(
        _('Name'),
        max_length=60,
        blank=False,
        unique=True,
        validators=[MinLengthValidator(3)],
        help_text=_('Required. 3 - 60 characters.')
    )

    def __str__(self):
        return str(self.name)
