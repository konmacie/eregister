from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from records.models import StudentGroup
from records.forms.group import GroupCreateForm, GroupUpdateForm


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
    form_class = GroupCreateForm
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
    form_class = GroupUpdateForm
    template_name = 'records/group/group_update.html'
    context_object_name = 'group'
    success_message = _("Group updated successfully")
