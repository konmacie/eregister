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
from django.core.exceptions import ValidationError
from records.models import StudentGroup
from records.forms import group as group_forms


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
        qs = qs.select_related('educator')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_assignments'] = self.object.get_current_assignments()
        return context


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
        current_assignments = self.object.get_current_assignments()
        out_of_date_assignments = self.object\
            .get_all_assignments()\
            .exclude(pk__in=current_assignments)
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


class AssignManyToGroupView(PermissionRequiredMixin, SuccessMessageMixin,
                            SingleObjectMixin, FormView):
    permission_required = ['records.add_studentgroupassignment']
    model = StudentGroup
    form_class = group_forms.AssignManyToGroupForm
    template_name = 'records/group/assign_many_to_group.html'
    context_object_name = 'group'
    success_message = _('Students assigned successfully')

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
        try:
            with transaction.atomic():
                """ Assign students to group """
                for student in students_to_add:
                    assignment = StudentGroupAssignment(
                        student=student, **kwargs
                    )
                    assignment.full_clean()
                    assignment.save()
        except ValidationError as err:
            form.add_error(None, err)
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()
