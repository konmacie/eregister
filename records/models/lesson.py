from django.db import models
from django.utils.translation import gettext_lazy as _


class Lesson(models.Model):
    STATUS_PLANNED = 0
    STATUS_REALIZED = 1
    STATUS_CHOICES = [
        (STATUS_PLANNED, _('Planned')),
        (STATUS_REALIZED, _('Realized')),
    ]

    status = models.IntegerField(
        _('Status'),
        blank=False,
        null=False,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNED
    )

    schedule = models.ForeignKey(
        'records.Schedule',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name=_('Schedule entry'),
        related_name='lessons'
    )

    date = models.DateField(
        _('Date'),
        blank=False,
        null=False
    )

    subject = models.TextField(
        _('Subject'),
        blank=True
    )

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lesson')
        ordering = ['-date']
        unique_together = ['schedule', 'date']

    @property
    def realized(self):
        return self.status == self.STATUS_REALIZED

    @property
    def short_subject(self):
        subject = self.subject
        return subject if len(subject) < 100 else (subject[:95] + "(...)")

    @classmethod
    def from_dates(cls, schedule, dates):
        """ Bulk create Lessons from dates list"""
        objs = [Lesson(schedule=schedule, date=date) for date in dates]
        Lesson.objects.bulk_create(objs)

    def __str__(self):
        return str(self.date)
