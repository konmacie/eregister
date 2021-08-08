from records.models import Mark, User, Course
from django import forms


class MarkUpdateForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['symbol']


class MarkCreateForm(forms.ModelForm):
    """
    Form to create Mark, need provided students queryset as argument,
    and course and teacher in initial dict.
    """
    class Meta:
        model = Mark
        fields = '__all__'

    student = forms.ModelChoiceField(
        queryset=None,
        required=True
    )

    teacher = forms.ModelChoiceField(
        queryset=User.objects,
        disabled=True,
        widget=forms.HiddenInput()
    )

    course = forms.ModelChoiceField(
        queryset=Course.objects,
        disabled=True,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, students, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = students
