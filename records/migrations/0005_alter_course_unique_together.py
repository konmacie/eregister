# Generated by Django 3.2.4 on 2021-07-20 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0004_course_period_schedule'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='course',
            unique_together={('name', 'group')},
        ),
    ]
