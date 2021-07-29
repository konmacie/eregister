import datetime
from collections import OrderedDict
from records.models import Lesson, Period


def get_teacher_timetable(dates, teacher):
    """
    Return teacher's timetable in form of OrderedDict with Periods as keys
    and lists of Lesson|None (if no Lesson on that day) as items,
    where first Lesson is related to first date provided in 'dates' parameter,
    second Lesson to second date, etc., meaning one key and corresponding
    item makes one row of timetable.
    """
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


def get_group_timetable(dates, group):
    """
    Return groups's timetable in form of OrderedDict with Periods as keys
    and lists of Lesson|None (if no Lesson on that day) as items,
    where first Lesson is related to first date provided in 'dates' parameter,
    second Lesson to second date, etc., meaning one key and corresponding
    item makes one row of timetable.
    """
    timetable = OrderedDict()
    periods = list(Period.objects.all())
    days = len(dates)

    for period in periods:
        timetable[period] = [None] * days

    for index, date in enumerate(dates):
        lessons = Lesson.objects.filter(
            date=date,
            schedule__course__group=group
        ).select_related('schedule', 'schedule__teacher', 'schedule__course',
                         'schedule__course__group')
        for lesson in list(lessons):
            timetable[lesson.schedule.period][index] = lesson
    return timetable


def get_lessons_table(teacher, date=None):
    if not date:
        date = datetime.date.today()

    table = OrderedDict()

    for period in Period.objects.all():
        table[period] = None

    lessons = Lesson.objects.filter(
        date=date,
        schedule__teacher=teacher
    ).select_related('schedule', 'schedule__course', 'schedule__course__group',
                     'schedule__period')
    for lesson in lessons:
        table[lesson.schedule.period] = lesson
    return table
