from django.urls import path
from records.views import student as student_views

app_name = 'student'
urlpatterns = [
    path('list/',
         student_views.StudentListView.as_view(),
         name='list'),
    path('new/',
         student_views.StudentCreateView.as_view(),
         name='create'),
    path('<pk>/',
         student_views.StudentDetailView.as_view(),
         name='detail'),
]
