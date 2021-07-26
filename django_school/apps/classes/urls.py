from django.urls import path

from django_school.apps.classes.views import ClassesListView

app_name = "classes"

urlpatterns = [
    path("list/", ClassesListView.as_view(), name="list"),
]
