from records.models import mark
from django.db import models
from django.utils.translation import gettext_lazy as _


class ChangeHistory(models.Model):
    TYPE_ADD = 0
    TYPE_MODIFY = 1
    TYPE_ERASE = 2
    TYPE_CHOICES = [
        (TYPE_ADD, _('Add')),
        (TYPE_MODIFY, _('Modify')),
        (TYPE_ERASE, _('Erase')),
    ]

    mark = models.ForeignKey(
        'records.Mark',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    type = models.IntegerField(
        _('Type'),
        blank=False,
        null=False,
        choices=TYPE_CHOICES
    )

    user = models.ForeignKey(
        'records.User',
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        limit_choices_to={'is_teacher': True},
    )

    value_old = models.ForeignKey(
        'records.Symbol',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('Old value'),
        related_name='+'
    )

    value_new = models.ForeignKey(
        'records.Symbol',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('New value'),
        related_name='+'
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Mark change history')
        verbose_name_plural = _('Mark change history')
        ordering = ['-timestamp']
