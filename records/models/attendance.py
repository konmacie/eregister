from django.db import models
from django.utils.translation import gettext_lazy as _


class Attendance(models.Model):
    STATUS_PRESENT = 0
    STATUS_LATE = 1
    STATUS_ABSENT = 2

    STATUS_CHOICES = [
        (STATUS_PRESENT, _('Present')),
        (STATUS_LATE, _('Late')),
        (STATUS_ABSENT, _('Absent')),
    ]

    status = models.IntegerField(
        _('Status'),
        blank=False,
        null=False,
        choices=STATUS_CHOICES,
        default=STATUS_PRESENT
    )

    lesson = models.ForeignKey(
        'records.Lesson',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='attendances'
    )

    student = models.ForeignKey(
        'records.User',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='attendances'
    )

    class Meta:
        verbose_name = _('Attendance')
        verbose_name_plural = _('Attendances')
        unique_together = ['lesson', 'student']
        ordering = ['-lesson__date',
                    'student__last_name', 'student__first_name']
