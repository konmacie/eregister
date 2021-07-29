from django.urls import path
from records.views import lesson as lesson_views

app_name = 'lesson'
urlpatterns = [
    path('realized/',
         lesson_views.RealizedLessonsListView.as_view(),
         name='realized'),
    path('unrealized/',
         lesson_views.UnrealizedLessonsListView.as_view(),
         name='unrealized'),
    path('cancelled/',
         lesson_views.CancelledLessonsListView.as_view(),
         name='cancelled'),
    path('<pk>/',
         lesson_views.LessonUpdateView.as_view(),
         name='update'),

]
