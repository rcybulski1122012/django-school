from django.urls import path

from django_school.apps.classes.views import ClassDetailView, ClassesListView

app_name = "classes"

urlpatterns = [
    path("", ClassesListView.as_view(), name="list"),
    path("<slug:slug>/", ClassDetailView.as_view(), name="detail"),
]
