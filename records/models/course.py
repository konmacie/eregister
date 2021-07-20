from django.db import models
from django.utils.translation import gettext_lazy as _


class Course(models.Model):
    name = models.CharField(
        _('Name'),
        max_length=50,
        blank=False,
        null=False
    )

    group = models.ForeignKey(
        'records.StudentGroup',
        verbose_name=_('Student group'),
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name='courses'
    )

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['name']
        unique_together = ['name', 'group']

    def __str__(self):
        return str(self.name)
