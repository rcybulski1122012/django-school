from django.urls import path

from django_school.apps.classes.views import ClassDetailView, ClassListView

app_name = "classes"

urlpatterns = [
    path("", ClassListView.as_view(), name="list"),
    path("<slug:class_slug>/", ClassDetailView.as_view(), name="detail"),
]
