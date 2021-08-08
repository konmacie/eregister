from django.http.response import HttpResponseRedirect
from django.views.generic import ListView, UpdateView, DetailView
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, UserPassesTestMixin)
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from records.models import Lesson, Attendance, Mark, User
from records.forms import attendance as attendance_forms
from records.forms import mark as mark_forms
from records.views.mixins import PrevURLMixin
import datetime
from collections import OrderedDict


class LessonUpdateView(PermissionRequiredMixin, UserPassesTestMixin,
                       PrevURLMixin, UpdateView):
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
        if self.request.method in ('POST', 'PUT') and \
                'restore_lesson' not in self.request.POST:
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return attendance_forms.AttendanceFormSet(**kwargs)

    def cancel_lesson(self):
        self.object.status = Lesson.STATUS_CANCELLED
        self.object.subject = ""
        self.object.save()
        self.object.sync_attendances()
        messages.success(
            self.request, _('Lesson cancelled successfuly.')
        )
        if self.prev_url:
            return HttpResponseRedirect(self.prev_url)
        return self.handle_cancelled()

    def restore_lesson(self):
        self.object.status = Lesson.STATUS_PLANNED
        self.object.save()
        self.object.sync_attendances()
        messages.success(
            self.request, _('Lesson restored successfuly.')
        )
        return self.render_to_response(self.get_context_data())

    def handle_cancelled(self):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """ Validate Lesson form and Attendances formset"""
        self.object = self.get_object()

        # check if user cancelled or restored lesson
        if 'restore_lesson' in request.POST and self.object.is_cancelled:
            return self.restore_lesson()
        elif 'cancel_lesson' in request.POST and not self.object.is_cancelled:
            return self.cancel_lesson()

        # if lesson is cancelled and yet user sent POST data,
        # skip validating it and don't save object
        if self.object.is_cancelled:
            return self.handle_cancelled()

        # validate forms and save lesson
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
        if 'formset' not in kwargs:
            kwargs['formset'] = self.get_formset()
        return super().get_context_data(**kwargs)


class LessonMarksView(PermissionRequiredMixin, UserPassesTestMixin,
                      PrevURLMixin, DetailView):
    permission_required = ['records.change_lesson']
    model = Lesson
    template_name = 'records/lesson/lesson_marks.html'
    context_object_name = 'lesson'

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
            .exclude(status=Lesson.STATUS_CANCELLED)\
            .select_related('schedule', 'schedule__teacher',
                            'schedule__period', 'schedule__course',
                            'schedule__course__group')
        return qs

    def _get_marks(self):
        students = OrderedDict()
        course = self.object.schedule.course
        for attendance in self.object.attendances.all():
            absent = (attendance.status == Attendance.STATUS_ABSENT)
            marks = Mark.objects.filter(
                student=attendance.student,
                course=course
            ).select_related('symbol')
            students[attendance.student] = {
                'marks': list(marks),
                'absent': absent
            }
        return students

    def _get_mark_create_form(self):
        initial = {
            'teacher': self.request.user,
            'course': self.object.schedule.course
        }
        students_pks = self.object.attendances.all().values_list(
            'student', flat=True
        )
        students = User.objects.filter(pk__in=students_pks)
        form = mark_forms.MarkCreateForm(
            students=students,
            initial=initial,
            prefix='create'
        )
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = self._get_marks()
        context['form'] = self._get_mark_create_form()
        return context


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
            .filter(status=Lesson.STATUS_CANCELLED)
        return qs
