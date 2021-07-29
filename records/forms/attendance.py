from django.forms import modelformset_factory, ModelForm, RadioSelect
from records.models import Attendance


class AttendanceForm(ModelForm):
    class Meta:
        model = Attendance
        fields = ['status']
        widgets = {
            'status': RadioSelect(attrs={'class': 'form-check-input me-1'}),
        }


AttendanceFormSet = modelformset_factory(
    Attendance,
    form=AttendanceForm,
    extra=0,
)
