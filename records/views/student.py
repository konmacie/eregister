from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from records.forms.student import StudentCreateForm

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

    def get_queryset(self):
        """ Limit queryset to student accounts. """
        qs = super().get_queryset()
        return qs.filter(is_teacher=False)


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

    def get_queryset(self):
        """ Limit queryset to users without teacher status. """
        qs = super().get_queryset()
        return qs.filter(is_teacher=False)

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
