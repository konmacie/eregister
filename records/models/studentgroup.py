from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings
from datetime import date


class StudentGroup(models.Model):
    """
    Group of Users without teacher status.
    - StudentGroup_obj.educator - User object set as educator
    """
    class Meta:
        verbose_name = _('Student group')
        verbose_name_plural = _('Student groups')
        ordering = ['name', ]

    name = models.CharField(
        _('Name'),
        blank=False,
        unique=True,
        max_length=30,
    )

    # Educator responsible for the group.
    # Limit choices to Users with is_teacher set to True
    educator = models.OneToOneField(
        verbose_name=_('Educator'),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        limit_choices_to={'is_teacher': True},
        related_name='educated_group'
    )

    def get_students_by_date(self, date):
        qs = self.assignments.filter(
            date_start__lte=date,
            date_end__gte=date,
        ).select_related('student')
        return qs

    def get_all_student(self):
        qs = self.assignments.select_related('student')
        return qs

    @property
    def students(self):
        return self.get_students_by_date(date.today())

    def get_absolute_url(self):
        """TODO"""
        pass

    def __str__(self) -> str:
        return str(self.name)


class StudentGroupAssignment(models.Model):
    class Meta:
        verbose_name = _('Group assignment')
        verbose_name_plural = _('Group assignments')
        ordering = ['student__last_name', 'student__first_name']

    student = models.ForeignKey(
        verbose_name=_('Student'),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        limit_choices_to={'is_teacher': False},
        related_name='assignments'
    )

    group = models.ForeignKey(
        verbose_name=_('Student group'),
        to=StudentGroup,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name='assignments'
    )

    date_start = models.DateField(
        _('Start date'),
        blank=False,
        null=False
    )

    date_end = models.DateField(
        _('End date'),
        blank=False,
        null=False
    )

    def clean(self):
        super().clean()

        # check if ending date is not earlier than start date
        if self.date_end < self.date_start:
            raise ValidationError({
                'date_end': _(
                    "End date can't be earlier than start date."
                )
            })

    def __str__(self):
        return "{} ({} - {})".format(
            self.group, self.date_start, self.date_end
        )
