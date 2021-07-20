from django.urls import path
from records.views import group as group_views

app_name = 'group'
urlpatterns = [
    path('list/',
         group_views.GroupListView.as_view(),
         name='list'),
    path('new/',
         group_views.GroupCreateView.as_view(),
         name='create'),
    path('<pk>/',
         group_views.GroupDetailView.as_view(),
         name='detail'),
    path('<pk>/assignments/',
         group_views.GroupAssignmentsView.as_view(),
         name='assignments'),
    path('<pk>/update/',
         group_views.GroupUpdateView.as_view(),
         name='update'),
    path('<pk>/assign-students/',
         group_views.AssignManyToGroupView.as_view(),
         name='assign-many'),
    path('assignment/<pk>/',
         group_views.AssignmentUpdateView.as_view(),
         name='assign-update'),
    path('<pk>/courses/',
         group_views.GroupCoursesView.as_view(),
         name='courses'),
    path('<pk>/courses/new/',
         group_views.CourseCreateView.as_view(),
         name='course-create'),
    path('course/<pk>/',
         group_views.CourseUpdateView.as_view(),
         name='course-update'),
]
