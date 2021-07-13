from django.urls import path
from schedule.views import misc

urlpatterns = [
    path('', misc.DashboardView.as_view(), name='dashboard'),
]
