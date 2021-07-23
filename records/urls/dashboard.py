from django.urls import path
from records.views import dashboard as dashboard_views

app_name = 'dashboard'
urlpatterns = [
    path('', dashboard_views.DashboardRedirectView.as_view(), name='start'),
    path('teacher/',
         dashboard_views.TeacherDashboardView.as_view(),
         name='teacher'),
]
