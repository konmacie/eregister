from django import forms
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from records.utils.user import get_students_without_group
from records.models import StudentGroup

User = get_user_model()


class GroupCreateForm(forms.ModelForm):
    """
    'educator' field is limited to teachers without StudentGroup assigned.
    """
    educator = forms.ModelChoiceField(
        queryset=User.objects.filter(
            educated_group=None, is_teacher=True),
        required=True
    )

    class Meta:
        model = StudentGroup
        fields = ['name', 'educator']


class GroupUpdateForm(forms.ModelForm):
    """
    'educator' field is limited to teachers without StudentGroup assigned
    and current group's educator.
    """
    educator = forms.ModelChoiceField(
        queryset=None,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['educator'].queryset = User.objects.filter(
            Q(educated_group=None, is_teacher=True)
            | Q(pk=self.instance.educator.pk)
        )
        self.fields['educator'].initial = self.instance.educator

    class Meta:
        model = StudentGroup
        fields = ['name', 'educator']


class AssignManyToGroupForm(forms.Form):
    """
    Assign multiple students to group.
    Limit select choices to students not assigned to StudentGroup.
    """
    students_to_add = forms.ModelMultipleChoiceField(
        queryset=get_students_without_group(),
        label=_('Students'),
        help_text=_(
            "Only students currently not assigned to any group are shown. "
            "Students with up-to-date assignment, "
            "can be edited from their profile."
        ),
        required=True,
    )

    date_start = forms.DateField(
        label=_('Start date'),
        required=True,
    )

    date_end = forms.DateField(
        label=_('End date'),
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()

        d_start = cleaned_data.get('date_start')
        d_end = cleaned_data.get('date_end')
        if d_end < d_start:
            raise ValidationError({
                'date_end': _(
                    "End date can't be earlier than start date."
                )
            })
