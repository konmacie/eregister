from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from records.utils.schedule import get_lessons_table


class DashboardRedirectView(LoginRequiredMixin, RedirectView):
    """
    Redirect user's with teacher status to teacher dashboard,
    student to student dashboard.
    """

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_teacher:
            return reverse_lazy('dashboard:teacher')
        else:
            pass  # TODO: student's dashboard


class TeacherDashboardView(LoginRequiredMixin, UserPassesTestMixin,
                           TemplateView):
    template_name = "records/dashboard/teacher_dashboard.html"

    def test_func(self):
        return self.request.user.is_teacher

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = get_lessons_table(self.request.user)
        return context
