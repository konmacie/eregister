from django.db import models
from django.utils.translation import gettext_lazy as _


class Mark(models.Model):
    student = models.ForeignKey(
        "records.User",
        limit_choices_to={'is_teacher': False},
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name='marks',
        help_text=_("Required")
    )

    teacher = models.ForeignKey(
        "records.User",
        limit_choices_to={'is_teacher': True},
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )

    course = models.ForeignKey(
        "records.Course",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name='marks'
    )

    category = models.ForeignKey(
        "records.Category",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        help_text=_("Required")
    )

    symbol = models.ForeignKey(
        "records.Symbol",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        help_text=_("Required")
    )

    # TODO: erased bool field

    date_created = models.DateTimeField(
        auto_now_add=True,
    )

    date_modified = models.DateTimeField(
        auto_now=True,
    )

    # attributes used in pre and post_save signals to save change history
    modifying_user = None
    value_old = None

    class Meta:
        verbose_name = _('Mark')
        verbose_name_plural = _('Marks')
        ordering = ['student__last_name', 'student__first_name',
                    'date_created']

    def __str__(self):
        return str(self.symbol)
