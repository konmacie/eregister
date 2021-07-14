from django import forms
from django.contrib.auth import get_user_model

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
