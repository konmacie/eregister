from django.urls import path
from records.views import misc

urlpatterns = [
    path('', misc.DashboardView.as_view(), name='dashboard'),
]
