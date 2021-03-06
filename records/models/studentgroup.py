from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()


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

    def get_assignments_by_date(self, date=None):
        """
        Return queryset of assignments to the group for specific date,
        if date param not supplied, datetime.date.today() used
        """
        if not date:
            date = datetime.date.today()
        qs = self.assignments.filter(
            date_start__lte=date,
            date_end__gte=date,
        ).select_related('student')
        return qs

    def get_all_assignments(self):
        """
        Return queryset for all assignemts to the group,
        including out of date assignments
        """
        qs = self.assignments.select_related('student')
        return qs

    def get_students_by_date(self, date=None):
        """
        Return queryset of students assigned to the group on specific date,
        if date param not supplied, datetime.date.today() used
        """
        if not date:
            date = datetime.date.today()
        assignments = self.get_assignments_by_date(date)
        current_students = User.objects.filter(
            assignments__in=assignments)
        return current_students

    def get_all_students(self):
        """
        Return queryset of all students assigned to the group,
        including out of date assignments
        """
        all_students = User.objects.filter(
            assignments__in=self.assignments.all()
        ).distinct()
        return all_students

    @property
    def current_assignments(self): return self.get_assignments_by_date()

    @property
    def current_students(self): return self.get_students_by_date()

    def get_absolute_url(self):
        return reverse_lazy('group:detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return str(self.name)


class StudentGroupAssignment(models.Model):
    class Meta:
        verbose_name = _('Group assignment')
        verbose_name_plural = _('Group assignments')
        ordering = ['student__last_name', 'student__first_name', 'date_start']

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

    def _get_colliding_assignments(self):
        qs = StudentGroupAssignment.objects.filter(
            student=self.student,
            date_start__lte=self.date_end,
            date_end__gte=self.date_start
        ).select_related('student', 'group')
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        return qs

    def clean(self):
        super().clean()

        # check if ending date is not earlier than start date
        if self.date_end < self.date_start:
            raise ValidationError({
                'date_end': _(
                    "End date can't be earlier than start date."
                )
            })
        colliding_assignments = list(self._get_colliding_assignments())
        if colliding_assignments:
            raise ValidationError(
                _("Colliding assigments for %(student)s: %(collisions)s"),
                params={
                    'student': str(self.student),
                    'collisions': ", ".join(map(str, colliding_assignments)),
                }
            )

    def __str__(self):
        return "{} ({} - {})".format(
            self.group, self.date_start, self.date_end
        )
