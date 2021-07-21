from django.http.response import HttpResponseRedirect
from django.views.generic import CreateView, ListView, UpdateView, FormView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from records.models import Schedule, User
from records.forms import schedule as schedule_forms
from records.utils.dates import get_week_dates, get_weekday_names
from records.utils.schedule import get_teacher_timetable
from datetime import datetime


class TeacherTimetable(PermissionRequiredMixin, FormView):
    permission_required = ['records.view_schedule']
    form_class = schedule_forms.TeacherScheduleForm
    template_name = "records/schedule/teacher_timetable.html"
    timetable_kwargs = None

    def set_timetable_kwargs(self):
        teacher = self.kwargs.get('teacher', None)
        date = self.kwargs.get('date', None)
        full_week = self.kwargs.get('full_week', True)
        if teacher and date:
            self.timetable_kwargs = {
                'teacher': get_object_or_404(User, pk=teacher,
                                             is_teacher=True),
                'date': datetime.strptime(date, '%Y-%m-%d').date(),
                'full_week': bool(full_week)
            }
            print(self.timetable_kwargs)

    def get(self, request, *args, **kwargs):
        self.set_timetable_kwargs()
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self.timetable_kwargs:
            initial.update(self.timetable_kwargs)
        return initial

    def form_valid(self, form):
        kwargs = {
            'teacher': form.cleaned_data['teacher'].pk,
            'date': form.cleaned_data['date'],
            'full_week': int(form.cleaned_data['full_week'])
        }
        return HttpResponseRedirect(reverse_lazy(
            'schedule:timetable-teacher-specified',
            kwargs=kwargs
        ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.timetable_kwargs:
            if self.timetable_kwargs['full_week']:
                dates = get_week_dates(self.timetable_kwargs['date'])
            else:
                dates = [self.timetable_kwargs['date'], ]

            context['days'] = get_weekday_names(dates)
            context['timetable'] = get_teacher_timetable(
                dates, self.timetable_kwargs['teacher']
            )
        return context
