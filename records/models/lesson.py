from django.db import models
from django.utils.translation import gettext_lazy as _
from records.models import attendance
import datetime


class Lesson(models.Model):
    STATUS_PLANNED = 0
    STATUS_REALIZED = 1
    STATUS_CANCELED = 2
    STATUS_CHOICES = [
        (STATUS_PLANNED, _('Planned')),
        (STATUS_REALIZED, _('Realized')),
        (STATUS_CANCELED, _('Canceled')),
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

    subject = models.CharField(
        _('Subject'),
        blank=True,
        max_length=255,
    )

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['-date']
        unique_together = ['schedule', 'date']

    @property
    def is_realized(self):
        return self.status == self.STATUS_REALIZED

    @property
    def is_canceled(self):
        return self.status == self.STATUS_CANCELED

    @property
    def is_editable(self):
        return self.date <= datetime.date.today()

    @property
    def short_subject(self):
        subject = self.subject
        return subject if len(subject) < 100 else (subject[:95] + "(...)")

    @classmethod
    def from_dates(cls, schedule, dates):
        """ Bulk create Lessons from dates list"""
        objs = [Lesson(schedule=schedule, date=date) for date in dates]
        Lesson.objects.bulk_create(objs)

    def sync_attendances(self):
        """
        Create Attendances related to Lesson. If lesson is cancelled,
        delete all related attendances
        """

        # delete attendances for canxelled lesson and exit
        if self.is_canceled:
            self.attendances.all().delete()
            return

        # get list of students by date
        group = self.schedule.course.group
        students = group.get_students_by_date(self.date)

        # create list of students that don't have related Attendance created
        missing_attendances = list(students)
        for att in self.attendances.all():
            if att.student in missing_attendances:
                missing_attendances.remove(att.student)
            else:
                att.delete()

        # create missing Attendances
        for student in missing_attendances:
            attendance.Attendance(lesson=self, student=student).save()

    def __str__(self):
        return str(self.date)
