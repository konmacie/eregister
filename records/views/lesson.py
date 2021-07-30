from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, UserPassesTestMixin)
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from records.models import Lesson, Attendance
from records.forms import attendance as attendance_forms
import datetime


class LessonUpdateView(PermissionRequiredMixin, UserPassesTestMixin,
                       UpdateView):
    permission_required = ['records.change_lesson']
    model = Lesson
    template_name = 'records/lesson/lesson_update.html'
    context_object_name = 'lesson'
    success_message = _("Lesson saved successfully")
    prefix = 'lesson'
    fields = ['subject']

    def test_func(self):
        """ Test if User is selected lesson's teacher """
        self.object = self.get_object()
        return self.object.schedule.teacher == self.request.user

    def get_object(self, queryset=None):
        if not hasattr(self, 'object'):
            self.object = super().get_object(queryset=queryset)
            self.object.sync_attendances()
        return self.object

    def get_queryset(self):
        """ Limit editable lessons to ones with past/today date """
        qs = super().get_queryset()\
            .filter(date__lte=datetime.date.today())\
            .select_related('schedule', 'schedule__teacher',
                            'schedule__period', 'schedule__course',
                            'schedule__course__group')
        return qs

    def get_formset(self):
        """ Returns formset to check students' attendance """
        kwargs = {
            'prefix': 'attendances',
            'queryset': Attendance.objects.filter(lesson=self.object)
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return attendance_forms.AttendanceFormSet(**kwargs)

    def post(self, request, *args, **kwargs):
        """ Validate Lesson form and Attendances formset"""
        self.object = self.get_object()
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        """ Save Lesson instance and related Attendances """
        self.object = form.save(commit=False)
        if 'status_realized' in self.request.POST:
            self.object.status = Lesson.STATUS_REALIZED
        else:
            self.object.status = Lesson.STATUS_PLANNED
        self.object.save()
        formset.save()

        # add success message to request
        messages.success(self.request, self.success_message)

        # render view again with updated forms
        return self.render_to_response(self.get_context_data(
            form=form,
            formset=formset
        ))

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(
            form=form,
            formset=formset
        ))

    def get_context_data(self, **kwargs):
        prev = self.request.GET.get('prev', None)
        if prev:
            kwargs['prev'] = prev
        if 'formset' not in kwargs:
            kwargs['formset'] = self.get_formset()
        return super().get_context_data(**kwargs)


class AllLessonsListView(PermissionRequiredMixin, ListView):
    """
    List view with prefetched teacher, course, group etc. and filtered
    for current user.
    """
    permission_required = ['records.view_lesson']
    model = Lesson
    paginate_by = 20
    context_object_name = 'lessons'

    def get_queryset(self):
        qs = super().get_queryset()\
            .filter(schedule__teacher=self.request.user)\
            .select_related('schedule', 'schedule__teacher',
                            'schedule__period', 'schedule__course',
                            'schedule__course__group')
        return qs


class RealizedLessonsListView(AllLessonsListView):
    template_name = 'records/lesson/lesson_realized_list.html'

    def get_queryset(self):
        qs = super().get_queryset()\
            .filter(status=Lesson.STATUS_REALIZED,
                    date__lte=datetime.date.today())
        return qs


class UnrealizedLessonsListView(AllLessonsListView):
    template_name = 'records/lesson/lesson_unrealized_list.html'

    def get_queryset(self):
        qs = super().get_queryset()\
            .filter(status=Lesson.STATUS_PLANNED,
                    date__lte=datetime.date.today())
        return qs


class CancelledLessonsListView(AllLessonsListView):
    template_name = 'records/lesson/lesson_cancelled_list.html'

    def get_queryset(self):
        qs = super().get_queryset()\
            .filter(status=Lesson.STATUS_CANCELED)
        return qs
