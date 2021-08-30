from django.urls import path

from django_school.apps.grades.views import ClassGradesView, GradeCreateView

app_name = "grades"

urlpatterns = [
    path(
        "<slug:class_slug>/<slug:subject_slug>/add/",
        GradeCreateView.as_view(),
        name="add",
    ),
    path(
        "<slug:class_slug>/<slug:subject_slug>/",
        ClassGradesView.as_view(),
        name="class_grades",
    ),
]
