from django.urls import path
from records.views.ajax import mark as mark_views

app_name = 'ajax'
urlpatterns = [
    path('mark-details/',
         mark_views.MarkDetailView.as_view(),
         name="mark-details"),
    path('mark-update/<pk>/',
         mark_views.MarkUpdateView.as_view(),
         name="mark-update"),
    path('mark-create/lesson/<lesson>/',
         mark_views.MarkCreateView.as_view(),
         name="mark-create-lesson"),
]
