from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.deletion import PROTECT
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Schedule(models.Model):

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    DAYS_OF_WEEK = [
        (MONDAY, _('Monday')),
        (TUESDAY, _('Tuesday')),
        (WEDNESDAY, _('Wednesday')),
        (THURSDAY, _('Thursday')),
        (FRIDAY, _('Friday')),
        (SATURDAY, _('Saturday')),
        (SUNDAY, _('Sunday')),
    ]

    course = models.ForeignKey(
        'records.Course',
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('Course')
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'is_teacher': True},
        on_delete=PROTECT,
        blank=False,
        null=False,
        verbose_name=_('Teacher')
    )

    date_start = models.DateField(
        _('Start date'),
        blank=False,
        null=False
    )

    day_of_week = models.IntegerField(
        _('Day of the week'),
        blank=True,
        choices=DAYS_OF_WEEK
    )

    date_end = models.DateField(
        _('End date'),
        blank=False,
        null=False
    )

    period = models.ForeignKey(
        'records.Period',
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('Period')
    )

    class Meta:
        verbose_name = _('Schedule entry')
        verbose_name_plural = _('Schedule entry')
        ordering = ['-date_start']

    def _get_same_time_entries_qs(self):
        """
        Return queryset for schedule entries with same period and weekday,
        and overlaping dates
        """
        qs = Schedule.objects.filter(
            date_start__lte=self.date_end,
            date_end__gte=self.date_start,
            day_of_week=self.day_of_week,
            period=self.period
        ).select_related('teacher', 'course', 'period')
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        return qs

    def _get_collisions_by_group(self, qs=None):
        if not qs:
            qs = self._get_same_time_entries_qs()
        qs = qs.filter(course__group=self.course.group)
        return list(qs)

    def _get_collisions_by_teacher(self, qs=None):
        if not qs:
            qs = self._get_same_time_entries_qs()
        qs = qs.filter(teacher=self.teacher)
        return list(qs)

    def clean(self) -> None:
        super().clean()
        # check if ending date isn't earlier than starting date
        if self.date_end < self.date_start:
            raise ValidationError({
                'date_end': _("Ending date can't "
                              "be earlier than starting date.")
            })

        self.day_of_week = self.date_start.weekday()

        # check for collisions (if selected teacher or student group
        # already have planned lesson at that time)
        raise_error = False
        errors = {}
        qs = self._get_same_time_entries_qs()
        collisions_group = self._get_collisions_by_group(qs)
        collisions_teacher = self._get_collisions_by_group(qs)
        error_msg = _("Colliding entries: %(collisions)s")
        if collisions_group:
            errors['course'] = error_msg % {
                'collisions': "; ".join(map(str, collisions_group))
            }
            raise_error = True
        if collisions_teacher:
            errors['teacher'] = error_msg % {
                'collisions': "; ".join(map(str, collisions_teacher))
            }
            raise_error = True

        if raise_error:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return "{}, {}, {} ({}, {} - {})".format(
            self.course,
            self.course.group,
            self.teacher,
            self.period,
            self.date_start,
            self.date_end
        )