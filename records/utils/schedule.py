import datetime
from collections import OrderedDict
from records.models import Lesson, Period


def get_teacher_timetable(dates, teacher):
    timetable = OrderedDict()
    periods = list(Period.objects.all())
    days = len(dates)

    for period in periods:
        timetable[period] = [None] * days

    for index, date in enumerate(dates):
        lessons = Lesson.objects.filter(
            date=date,
            schedule__teacher=teacher
        ).select_related('schedule', 'schedule__teacher', 'schedule__course',
                         'schedule__course__group')
        for lesson in list(lessons):
            timetable[lesson.schedule.period][index] = lesson
    return timetable
