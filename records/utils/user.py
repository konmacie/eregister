from records.models import User, StudentGroup, StudentGroupAssignment
from datetime import date


def get_students_without_group():
    today = date.today()
    qs_students_in_group = User.objects.filter(
        assignments__date_start__lte=today,
        assignments__date_end__gte=today
    )
    # not working in sqlite (.difference() with .order_by())
    # return User.objects.all().difference(qs_students_in_group)
    return User.objects.filter(is_teacher=False)\
        .exclude(pk__in=qs_students_in_group)
