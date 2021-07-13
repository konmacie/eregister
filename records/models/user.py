from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.urls import reverse
from datetime import date


class User(AbstractUser):
    """
    Substitute for built-in User model, with required first/last name
    and autogenerated username.
    Additional bool is_teacher field.
    Additional optional fields:
        -birth_date -> Date
        -address -> char
        -zip_code -> char
        -city -> char
        -phone_number -> char
        -student_group -> ForeignKey(StudentGroup)
    New permissions: add_student, view_student, change_student, delete_student,
        reset_student_password
    """
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['last_name', 'first_name']
        permissions = [
            ('add_student', _('Can add Student')),
            ('view_student', _('Can view Student')),
            ('change_student', _('Can change Student')),
            ('delete_student', _('Can delete Student')),
            ('reset_student_password', _('Can reset Student\'s password')),
        ]

    # Make username unrequired. If left blank during creation/editing,
    # username will be generated by generate_username() called by
    # pre_save signal.
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Letters, digits and @/./+/-/_ only. '
            'Autogenerated if left blank.'),
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
        blank=True,
    )
    first_name = models.CharField(
        _('first name'), max_length=150, blank=False, null=False,
        help_text='Required.')
    last_name = models.CharField(
        _('last name'), max_length=150, blank=False, null=False,
        help_text='Required.')

    birth_date = models.DateField(
        _('Birth date'), blank=True, null=True)

    address = models.CharField(
        _('Address'), max_length=50, blank=True, null=True)
    zip_code = models.CharField(
        _('ZIP code'), max_length=10, blank=True, null=True)
    city = models.CharField(
        _('City'), max_length=50, blank=True, null=True)
    phone = models.CharField(
        _('Phone number'), max_length=15, blank=True, null=True)

    is_teacher = models.BooleanField(default=False)

    # Fields required during createsuperuser
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    @property
    def is_student(self) -> bool:
        return not self.is_teacher

    @property
    def is_educator(self) -> bool:
        return hasattr(self, 'educated_group')

    @property
    def student_group(self):
        """Return currently assigned student group or None"""
        today = date.today()
        qs = self.assignments.filter(
            date_start__lte=today,
            date_end__gte=today,
        ).select_related('group')
        assign = qs.first()
        if assign:
            return assign.group
        return None

    def clean(self) -> None:
        """
        Check if user is designated as group educator,
        before removing teacher status.
        """
        super().clean()
        if not self.is_teacher and self.is_educator:
            err_msg = _(
                "User is designated as educator of group {student_group}. "
                "Can\'t remove teacher status."
            ).format(student_group=self.educated_group)

            raise ValidationError(
                {'student_group': err_msg}
            )

    def get_absolute_url(self):
        return reverse("student:detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        """Return full name instead of username"""
        return self.get_full_name()
