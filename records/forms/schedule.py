from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from datetime import date

User = get_user_model()


class TeacherScheduleForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(is_teacher=True),
        required=True,
        empty_label=None
    )

    date = forms.DateField(
        initial=date.today,
        required=True
    )

    full_week = forms.BooleanField(
        initial=True,
        label=_('Show whole week'),
        required=False
    )
