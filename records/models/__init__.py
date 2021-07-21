from .user import User
from .studentgroup import StudentGroup, StudentGroupAssignment
from .course import Course
from .period import Period
from .schedule import Schedule
from .lesson import Lesson

from django.db.models.signals import pre_save, post_save
from records.signals.auth import generate_username
from records.signals.schedule import sync_lessons

pre_save.connect(generate_username, sender=User)
post_save.connect(sync_lessons, sender=Schedule)
