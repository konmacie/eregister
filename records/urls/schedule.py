from django.urls import path
from records.views import schedule as schedule_views

app_name = 'schedule'
urlpatterns = [
    path('',
         schedule_views.MyScheduleRedirectView.as_view(),
         name='timetable-my'),
    path('teacher/',
         schedule_views.TeacherTimetableView.as_view(),
         name='timetable-teacher'),
    path('teacher/<teacher>/<date>/<int:full_week>/',
         schedule_views.TeacherTimetableView.as_view(),
         name='timetable-teacher-specified'),
    path('group/',
         schedule_views.GroupTimetableView.as_view(),
         name='timetable-group'),
    path('group/<group>/<date>/<int:full_week>/',
         schedule_views.GroupTimetableView.as_view(),
         name='timetable-group-specified'),
    path('group/<group_pk>/add/',
         schedule_views.AddScheduleView.as_view(),
         name='add'),
    path('edit/<pk>/',
         schedule_views.EditScheduleView.as_view(),
         name='edit'),
]
