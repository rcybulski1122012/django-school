from django.urls import path

from django_school.apps.grades.views import GradeCreateView

app_name = "grades"

urlpatterns = [
    path("<slug:slug>/add/", GradeCreateView.as_view(), name="add"),
]
