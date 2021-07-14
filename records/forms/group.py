from django import forms
from django.db.models import Q
from django.contrib.auth import get_user_model
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
