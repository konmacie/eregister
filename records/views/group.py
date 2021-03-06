from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from records.models.studentgroup import StudentGroupAssignment
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.views.generic.edit import FormView
from django.db import transaction
from django.db.models import When, Case, Value
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from records.models import StudentGroup, Course
from records.forms import group as group_forms
from records.views.schedule import GroupTimetableView
from records.views.mixins import PrevURLMixin
import datetime

User = get_user_model()


class GroupListView(PermissionRequiredMixin, ListView):
    """
    View to show list of StudentGroups.
    Need 'records.view_studentgroup' permission to access.
    """
    permission_required = ['records.view_studentgroup']
    model = StudentGroup
    template_name = 'records/group/group_list.html'
    paginate_by = 20
    context_object_name = 'groups'

    def get_queryset(self):
        """ Prefetch educator """
        qs = super().get_queryset()
        return qs.select_related('educator')


class GroupDetailView(PermissionRequiredMixin, DetailView):
    """
    View showing StudentGroup's details.
    Need 'records.view_studentgroup' permission to access it.
    """
    permission_required = ['records.view_studentgroup']
    model = StudentGroup
    template_name = 'records/group/group_detail.html'
    context_object_name = 'group'

    def get_queryset(self):
        """ Prefetch educator """
        qs = super().get_queryset()
        return qs.select_related('educator')


class GroupAssignmentsView(PermissionRequiredMixin, DetailView):
    """
    View showing StudentGroup's details.
    Need 'records.view_studentgroup' permission to access it.
    """
    permission_required = ['records.view_studentgroup']
    model = StudentGroup
    template_name = 'records/group/group_assignments.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_assignments = self.object.current_assignments

        # annotate out of date assignments with Boolean 'future'
        # True for assignments with date_start later than actual date
        today = datetime.date.today()
        out_of_date_assignments = self.object\
            .get_all_assignments()\
            .exclude(pk__in=current_assignments)\
            .annotate(
                future=Case(
                    When(date_start__gt=today, then=Value(True)),
                    default=Value(False)
                )
            )
        context['current_assignments'] = current_assignments
        context['out_of_date_assignments'] = out_of_date_assignments
        return context


class GroupCreateView(PermissionRequiredMixin, SuccessMessageMixin,
                      CreateView):
    """
    View to create new StudentGroup.
    Need 'records.add_studentgroup' permission to access it.
    Uses custom GroupCreateForm, where educator field's queryset
    is limited to teachers without assigned group.
    """
    permission_required = ['records.add_studentgroup']
    model = StudentGroup
    form_class = group_forms.GroupCreateForm
    template_name = 'records/group/group_create.html'
    success_message = _("Group %(name)s created successfully")

    def get_success_url(self) -> str:
        """
        Depending on button clicked, redirect to group profile
        or to creation form again.
        """
        if 'save_and_add_next' in self.request.POST:
            return reverse_lazy('group:create')
        return super().get_success_url()


class GroupUpdateView(PermissionRequiredMixin, SuccessMessageMixin,
                      UpdateView):
    """
    View to update StudentGroup.
    Need 'records.change_studentgroup' permission to access it.
    Uses custom GroupUpdateForm, where educator field's queryset
    is limited to teachers without assigned group and current educator.
    """
    permission_required = ['records.change_studentgroup']
    model = StudentGroup
    form_class = group_forms.GroupUpdateForm
    template_name = 'records/group/group_update.html'
    context_object_name = 'group'
    success_message = _("Group updated successfully")


class AssignManyToGroupView(PermissionRequiredMixin,
                            SingleObjectMixin, FormView):
    """
    View to assign multiple students to a group.
    Depending on button clicked by user, skip students with colliding
    assignments and assign rest or display form again with error msg.
    """
    permission_required = ['records.add_studentgroupassignment']
    model = StudentGroup
    form_class = group_forms.AssignManyToGroupForm
    template_name = 'records/group/assign_many_to_group.html'
    context_object_name = 'group'
    success_message = _('%(count)i student(s) assigned successfully')
    warning_message = _(
        'Assignment ended with problems, '
        '%(count)i student(s) assigned successfully, '
        '%(err_count)i student(s) omitted.'
    )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        students_to_add = form.cleaned_data['students_to_add']
        kwargs = {
            'date_start': form.cleaned_data['date_start'],
            'date_end': form.cleaned_data['date_end'],
            'group': self.object
        }

        errors = []
        count = 0
        try:
            with transaction.atomic():
                # Assign students to group
                for student in students_to_add:
                    try:
                        assignment = StudentGroupAssignment(
                            student=student, **kwargs
                        )
                        assignment.full_clean()
                        assignment.save()
                        count += 1
                    except ValidationError as error:
                        errors.append(error)
                if errors and 'unsafe_add' not in self.request.POST:
                    # Raise error to rollback whole transaction,
                    # if user didn't select option to skip collissions
                    form.add_error(None, errors)
                    raise ValidationError(
                        _('Errors occurred during assignment'))
        except ValidationError as error:
            # Display errors and show form again if rollback occured
            messages.error(self.request, error.messages[0])
            return self.form_invalid(form)

        if errors:
            # show messages about skipped students
            messages.warning(
                self.request,
                self.warning_message % {
                    'count': count,
                    'err_count': len(errors)
                })
            for error in errors:
                messages.error(
                    self.request, error.messages[0], extra_tags='py-1')
        else:
            # show success msg if no skip occured
            messages.success(
                self.request,
                self.success_message % {
                    'count': count,
                }
            )
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class AssignmentUpdateView(PermissionRequiredMixin, SuccessMessageMixin,
                           PrevURLMixin, UpdateView):
    """
    View to edit group assignment
    """
    permission_required = ['records.change_studentgroupassignment']
    model = StudentGroupAssignment
    fields = ['date_start', 'date_end']
    template_name = 'records/group/assignment_update.html'
    context_object_name = 'assignment'
    success_message = _('Assignment updated successfully')

    def get_queryset(self):
        """ Prefetch student and educator """
        qs = super().get_queryset()
        return qs.select_related('student', 'group')

    def get_success_url(self):
        if self.prev_url:
            return self.prev_url
        return reverse_lazy('student:assignments',
                            kwargs={'pk': self.object.student.pk})


class GroupCoursesView(PermissionRequiredMixin, ListView):
    """
    View to show list of Courses for a StudentGroup.
    """
    permission_required = ['records.view_studentgroup']
    model = Course
    template_name = 'records/group/group_courses.html'
    paginate_by = 20
    context_object_name = 'courses'

    def _get_group(self):
        pk = self.kwargs.get('pk')
        group = get_object_or_404(StudentGroup, pk=pk)
        return group

    def get_queryset(self):
        qs = super().get_queryset()
        self.group = self._get_group()
        return qs.filter(group=self.group)

    def get_context_data(self, **kwargs):
        kwargs['group'] = self.group
        return super().get_context_data(**kwargs)


class CourseCreateView(PermissionRequiredMixin, SuccessMessageMixin,
                       CreateView):
    """
    View to create course for a group.
    """
    permission_required = ['records.add_course']
    model = Course
    form_class = group_forms.CourseCreateForm
    template_name = 'records/group/course_create.html'
    success_message = _('Course - %(name)s - created successfully')

    def _get_group(self):
        pk = self.kwargs.get('pk')
        group = get_object_or_404(StudentGroup, pk=pk)
        return group

    def get(self, request, *args, **kwargs):
        self.group = self._get_group()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.group = self._get_group()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['group'] = self.group
        return super().get_context_data(**kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['group'] = self.group
        return initial

    def get_success_url(self):
        return reverse_lazy('group:courses', kwargs={
            'pk': self.group.pk
        })


class CourseUpdateView(PermissionRequiredMixin, SuccessMessageMixin,
                       UpdateView):
    """
    View to update course
    """
    permission_required = ['records.change_course']
    model = Course
    fields = ['name']
    template_name = 'records/group/course_update.html'
    context_object_name = 'course'
    success_message = _('Course - %(name)s - updated successfully')

    def get_context_data(self, **kwargs):
        kwargs['group'] = self.object.group
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('group:courses', kwargs={
            'pk': self.object.group.pk
        })


class GroupScheduleView(GroupTimetableView):
    """
    View selected group's schedule
    """
    permission_required = [
        'records.view_studentgroup', 'records.view_schedule']
    form_class = group_forms.GroupDateScheduleForm
    template_name = "records/group/group_timetable.html"

    def set_timetable_kwargs(self):
        group_pk = self.kwargs.get('pk')
        self.group = get_object_or_404(StudentGroup, pk=group_pk)

        # get date from kwargs, today() if date not provided
        date = self.kwargs.get('date', None)
        if date:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = datetime.date.today()

        full_week = bool(self.kwargs.get('full_week', True))

        self.timetable_kwargs = {
            'group': self.group,
            'date': date,
            'full_week': full_week
        }

    def get_context_data(self, **kwargs):
        kwargs['group'] = self.group
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        kwargs = {
            'pk': self.kwargs.get('pk'),
            'date': form.cleaned_data['date'],
            'full_week': int(form.cleaned_data['full_week'])
        }
        return HttpResponseRedirect(reverse_lazy(
            'group:schedule-specified',
            kwargs=kwargs
        ))
