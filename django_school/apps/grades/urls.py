from django.urls import path

from django_school.apps.grades.views import GradeCreateView, class_grades_view

app_name = "grades"

urlpatterns = [
    path(
        "<slug:class_slug>/<slug:subject_slug>/add/",
        GradeCreateView.as_view(),
        name="add",
    ),
    path(
        "<slug:class_slug>/<slug:subject_slug>/",
        class_grades_view,
        name="class_grades",
    ),
]
