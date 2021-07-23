from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from datetime import date
from records.models import Schedule, StudentGroup

User = get_user_model()


class TeacherScheduleForm(forms.Form):
    """ Used for filtering teachers's schedule in Schedule section """
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


class GroupScheduleForm(forms.Form):
    """ Used for filtering group's schedule in Schedule section """
    group = forms.ModelChoiceField(
        queryset=StudentGroup.objects,
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


class ScheduleAddForm(forms.ModelForm):

    course = forms.ModelChoiceField(
        queryset=None,
        required=True
    )

    class Meta:
        model = Schedule
        fields = '__all__'

    def __init__(self, *args, group, **kwargs):
        super().__init__(*args, **kwargs)
        # limit choice to courses of selected group
        self.fields['course'].queryset = group.courses


class ScheduleRestrictedEditForm(forms.ModelForm):
    """
    Form for editing Schedule. If there are related lessons with realized
    status, limit editable fields to dates, block changes to course,
    teacher, period fields.
    """
    course = forms.ModelChoiceField(
        queryset=None,
        required=True
    )

    class Meta:
        model = Schedule
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # limit choice to courses of selected group
        group = self.instance.course.group
        self.fields['course'].queryset = group.courses

        # if there are realized lessons, limit editable fields to dates,
        # block changes to course, teacher, period
        if not self.instance.is_editable:
            disable_fields = ['course', 'teacher', 'period']
            for field in disable_fields:
                self.fields[field].disabled = True
