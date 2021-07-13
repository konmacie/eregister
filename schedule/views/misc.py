from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from records.utils.user import get_students_without_group


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Index view.
    """
    template_name = "dashboard.html"
