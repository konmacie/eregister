from django import forms
from django.contrib.auth import get_user_model
from django.db.models import fields
from records.models import StudentGroupAssignment

User = get_user_model()


class StudentCreateForm(forms.ModelForm):
    """
    Form used to create new student.
    Account is created without password. It can be generated in right view.
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'birth_date', 'address',
                  'zip_code', 'city', 'phone', 'email']
        widgets = {
            'birth_date': forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}),
        }


class AssignToGroupForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects,
        disabled=True,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = StudentGroupAssignment
        fields = '__all__'
