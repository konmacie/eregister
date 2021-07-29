
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseRedirect
from django.views.generic import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from records.models import Schedule, User, StudentGroup
from records.forms import schedule as schedule_forms
from records.utils.dates import get_week_dates, get_weekday_names
from records.utils.schedule import get_group_timetable, get_teacher_timetable
from datetime import datetime


class TimetableView(FormView):
    """
    Abstract view to show timetable.
    """
    timetable_kwargs = None

    def set_timetable_kwargs(self):
        raise NotImplementedError()

    def get_timetable(self, dates):
        raise NotImplementedError()

    def form_valid(self, form):
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        self.set_timetable_kwargs()
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self.timetable_kwargs:
            initial.update(self.timetable_kwargs)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.timetable_kwargs:
            if self.timetable_kwargs['full_week']:
                dates = get_week_dates(self.timetable_kwargs['date'])
            else:
                dates = [self.timetable_kwargs['date'], ]

            context['days'] = get_weekday_names(dates)
            context['timetable'] = self.get_timetable(dates)
        return context


class TeacherTimetableView(PermissionRequiredMixin, TimetableView):
    """ View showing selected teacher's schedule """
    permission_required = ['records.view_schedule']
    form_class = schedule_forms.TeacherScheduleForm
    template_name = "records/schedule/teacher_timetable.html"

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

    def get_timetable(self, dates):
        return get_teacher_timetable(
            dates, self.timetable_kwargs['teacher']
        )

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


class GroupTimetableView(PermissionRequiredMixin, TimetableView):
    """ View showing selected group's schedule """
    permission_required = ['records.view_schedule']
    form_class = schedule_forms.GroupScheduleForm
    template_name = "records/schedule/group_timetable.html"

    def set_timetable_kwargs(self):
        group = self.kwargs.get('group', None)
        date = self.kwargs.get('date', None)
        full_week = self.kwargs.get('full_week', True)
        if group and date:
            self.timetable_kwargs = {
                'group': get_object_or_404(StudentGroup, pk=group),
                'date': datetime.strptime(date, '%Y-%m-%d').date(),
                'full_week': bool(full_week)
            }

    def get_timetable(self, dates):
        return get_group_timetable(
            dates, self.timetable_kwargs['group']
        )

    def form_valid(self, form):
        kwargs = {
            'group': form.cleaned_data['group'].pk,
            'date': form.cleaned_data['date'],
            'full_week': int(form.cleaned_data['full_week'])
        }
        return HttpResponseRedirect(reverse_lazy(
            'schedule:timetable-group-specified',
            kwargs=kwargs
        ))


class AddScheduleView(PermissionRequiredMixin, SuccessMessageMixin,
                      CreateView):
    """ View to add new schedule entry """
    permission_required = ['records.add_schedule']
    form_class = schedule_forms.ScheduleAddForm
    template_name = "records/schedule/schedule_add.html"
    success_message = _('Schedule created successfully')

    def get_group(self):
        group_pk = self.kwargs.get('group_pk')
        return get_object_or_404(StudentGroup, pk=group_pk)

    def get(self, request, *args, **kwargs):
        self.group = self.get_group()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.group = self.get_group()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['group'] = self.group
        kwargs['next'] = self.request.GET.get('next', None)
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['group'] = self.group
        return kwargs

    def get_success_url(self):
        next = self.request.GET.get('next', None)
        return next or super().get_success_url()


class EditScheduleView(PermissionRequiredMixin, SuccessMessageMixin,
                       UpdateView):
    permission_required = ['records.change_schedule']
    model = Schedule
    form_class = schedule_forms.ScheduleRestrictedEditForm
    template_name = 'records/schedule/schedule_update.html'
    context_object_name = 'schedule'
    success_message = _('Schedule updated successfully')

    def form_valid(self, form):
        # ValidationError can be raised by Schedule's save() if there
        # are realized lessons not in range of new dates.
        try:
            return super().form_valid(form)
        except ValidationError as err:
            form.add_error(None, err)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        kwargs['next'] = self.request.GET.get('next', None)
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        next = self.request.GET.get('next', None)
        return next or super().get_success_url()
