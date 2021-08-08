from .user import User
from .studentgroup import StudentGroup, StudentGroupAssignment
from .course import Course
from .period import Period
from .schedule import Schedule
from .lesson import Lesson
from .attendance import Attendance
from .mark import *

from django.db.models.signals import pre_save, post_save
from records.signals.auth import generate_username
from records.signals.schedule import sync_lessons
from records.signals.mark import mark_history_pre_save, mark_history_post_save

# generate username for user without one
pre_save.connect(generate_username, sender=User)

# create new and delete obsolete Lesson instances for saved Schedule
post_save.connect(sync_lessons, sender=Schedule)

# save mark change history
pre_save.connect(mark_history_pre_save, sender=Mark)
post_save.connect(mark_history_post_save, sender=Mark)
