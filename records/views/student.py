from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import When, Case, Value
from django.shortcuts import get_object_or_404
from records.forms.student import StudentCreateForm, AssignToGroupForm
from records.models import StudentGroupAssignment, Mark
import datetime

User = get_user_model()


class StudentListView(PermissionRequiredMixin, ListView):
    """
    View to show list of students.
    Need 'records.view_student' permission to access.
    """
    permission_required = ['records.view_student']
    model = User
    template_name = 'records/student/student_list.html'
    paginate_by = 20
    context_object_name = 'students'
    queryset = User.objects.filter(is_teacher=False)


class StudentDetailView(PermissionRequiredMixin, DetailView):
    """
    View showing student's details.
    Need 'records.view_student' permission to access it.
    If user have 'records.reset_student_password' permission,
    form to reset student's password is shown. Password reset is
    handled in post() method.
    """
    permission_required = ['records.view_student']
    model = User
    template_name = 'records/student/student_detail.html'
    context_object_name = 'student'
    queryset = User.objects.filter(is_teacher=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_group'] = self.object.student_group
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests. It's used to reset student's password.
        Need 'records.reset_student_password' permission to access.
        """
        # check if user has needed permission
        if not self.request.user.has_perms(
            ['records.reset_student_password']
        ):
            return self.handle_no_permission()

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        # reset student's password
        if 'generate_password' in request.POST:
            password = User.objects.make_random_password()
            self.object.set_password(password)
            self.object.save()
            # add password to context so it could be shown in template
            context['password'] = password
            # messages.success(self.request,
            #                  _('Password reset was successful'))
        return self.render_to_response(context)


class StudentCreateView(PermissionRequiredMixin, SuccessMessageMixin,
                        CreateView):
    """
    View to create new student account.
    Need 'records.add_student' permission to access.
    """
    permission_required = ['records.add_student']
    form_class = StudentCreateForm
    template_name = 'records/student/student_create.html'
    success_message = _(
        "Student %(last_name)s %(first_name)s added successfully")

    def get_success_url(self) -> str:
        """
        Depending on button clicked, redirect to student profile
        or to creation form again.
        """
        if 'save_and_add_next' in self.request.POST:
            return reverse_lazy('student:create')
        return super().get_success_url()


class StudentUpdateView(PermissionRequiredMixin, SuccessMessageMixin,
                        UpdateView):
    """
    View to edit student account.
    Need 'records.change_student' permission to access.
    """
    permission_required = ['records.change_student']
    model = User
    queryset = User.objects.filter(is_teacher=False)
    form_class = StudentCreateForm
    template_name = 'records/student/student_update.html'
    context_object_name = 'student'
    success_message = _("Student profile updated successfully")

    def get_success_url(self):
        """
        Depending on button clicked, redirect to student profile
        or to change form again.
        """
        if 'save_and_continue' in self.request.POST:
            return reverse_lazy('student:update',
                                kwargs={'pk': self.object.pk})
        return super().get_success_url()


class StudentAssignmentsView(PermissionRequiredMixin, DetailView):
    """
    View showing list of student's assignments.
    Need 'records.view_studentgroup' permission to access it.
    """
    permission_required = ['records.view_student']
    model = User
    queryset = User.objects\
        .filter(is_teacher=False)\
        .prefetch_related('assignments')
    template_name = 'records/student/student_assignments.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # annotate out of date assignments with Boolean 'future'
        # True for assignments with date_start later than actual date
        today = datetime.date.today()
        out_of_date_assignments = self.object.assignments\
            .select_related('group')\
            .annotate(
                future=Case(
                    When(date_start__gt=today, then=Value(True)),
                    default=Value(False)
                )
            )
        current_assignment = self.object.get_current_assignment()
        if current_assignment:
            out_of_date_assignments = out_of_date_assignments.exclude(
                pk=current_assignment.pk)
        context['current_assignment'] = current_assignment
        context['out_of_date_assignments'] = out_of_date_assignments
        return context


class AssignToGroupView(PermissionRequiredMixin, SuccessMessageMixin,
                        CreateView):
    """
    View to assign student to a group.
    """
    permission_required = ['records.add_studentgroupassignment']
    model = StudentGroupAssignment
    form_class = AssignToGroupForm
    template_name = 'records/student/assign_to_group.html'
    success_message = _('%(student)s assigned successfully to %(group)s')

    def _get_student(self):
        pk = self.kwargs.get('pk')
        student = get_object_or_404(User, pk=pk, is_teacher=False)
        return student

    def get(self, request, *args, **kwargs):
        self.student = self._get_student()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.student = self._get_student()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['student'] = self.student
        return super().get_context_data(**kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['student'] = self.student
        return initial

    def get_success_url(self):
        return reverse_lazy('student:assignments', kwargs={
            'pk': self.student.pk
        })


class StudentMarksView(PermissionRequiredMixin, DetailView):
    permission_required = ['records.view_student']
    model = User
    template_name = 'records/student/student_marks.html'
    context_object_name = 'student'
    queryset = User.objects.filter(is_teacher=False)

    def get_marks(self):
        qs = Mark.objects\
            .filter(student=self.object)\
            .order_by('course__group', 'course__name', 'date_created')\
            .select_related('symbol', 'course')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marks'] = self.get_marks()
        context['current_group'] = self.object.student_group
        return context
