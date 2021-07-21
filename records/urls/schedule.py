from django.urls import path
from records.views import schedule as schedule_views

app_name = 'schedule'
urlpatterns = [
    path('teacher/',
         schedule_views.TeacherTimetable.as_view(),
         name='timetable-teacher'),
    path('teacher/<teacher>/<date>/<int:full_week>/',
         schedule_views.TeacherTimetable.as_view(),
         name='timetable-teacher-specified'),
]
