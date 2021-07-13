import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eregister.settings')

import django
django.setup()

from django.contrib.auth.models import Group
from records.models import StudentGroup, User

from faker import Faker
fake = Faker()

import random
import logging
logger = logging.getLogger(__name__)

NUM_GROUPS = 5
NUM_TEACHERS = 15
NUM_STUDENTS = 100
VERBOSE = True

def add_student():
    kwargs = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "is_teacher": False,
        "defaults": {
            "birth_date": fake.date(),
            "address": fake.street_address(),
            "zip_code": fake.postcode(),
            "city": fake.city(),
            "phone": fake.msisdn(),
            "email": fake.email(),
        }
    }
    created = False
    while(not created):
        student, created = User.objects.get_or_create(**kwargs)
    if VERBOSE:
        logger.info("\t%s" % student.get_full_name())
    return student


if __name__ == "__main__":
    if VERBOSE:
        logger.info("Students:")
    for _ in range(NUM_STUDENTS):
        add_student()