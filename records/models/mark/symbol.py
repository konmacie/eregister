from django.db import models
from django.utils.translation import gettext_lazy as _


class Symbol(models.Model):
    class Meta:
        verbose_name = _('Symbol')
        verbose_name_plural = _('Symbols')
        ordering = ['name']

    name = models.CharField(
        _('Name'),
        max_length=5,
        blank=False,
        help_text=_('Required. 1 - 5 characters.')
    )

    value = models.DecimalField(
        _('Value'),
        max_digits=3,
        decimal_places=2,
        blank=False,
        help_text=_('Required. From 0 to 9.99.')
    )

    class Meta:
        verbose_name = _('Symbol')
        verbose_name_plural = _('Symbols')
        ordering = ['value']

    def __str__(self):
        return str(self.name)
