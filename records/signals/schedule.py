from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from records.models import Lesson
from records.utils.dates import get_dates_between, dates_diff


def sync_lessons(sender, instance, created, **kwargs):
    """
    For newly created Schedule, create all Lesson instances.
    For already existing Schedules, create missing Lessons for new dates
    and delete Lessons outside new dates range. If any of deleted Lessons
    has status = Realized raise ValidationError
    """
    # get list of new dates
    new_dates = get_dates_between(
        start_date=instance.date_start,
        end_date=instance.date_end
    )
    if created:
        # bulk create Lessons from dates list
        Lesson.from_dates(instance, new_dates)
    else:
        # get dates of Lessons existing in db
        old_dates = instance.lessons.values_list('date', flat=True)

        # get lists of dates that need Lesson created, and dates that need
        # Lesson instance deleted
        to_create, to_delete = dates_diff(new_dates, old_dates)

        # check for realized Lessons in instances to delete
        to_delete_qs = instance.lessons.filter(date__in=to_delete)
        to_delete_realized = to_delete_qs.filter(status=Lesson.STATUS_REALIZED)
        if to_delete_realized.exists():
            # raise ValidationError if any exists
            realized_lessons = list(to_delete_realized)
            error_msg = _(
                "Invalid dates - realized lessons out of range: "
                "%(realized)s"
            ) % {'realized': ", ".join(map(str, realized_lessons))}
            raise ValidationError({
                'date_end': error_msg
            })

        # delete redundant Lessons and create missing ones
        to_delete_qs.delete()
        Lesson.from_dates(instance, to_create)
