from django.urls import path

from django_school.apps.grades.views import (ClassGradesView, GradeCreateView,
                                             GradeDeleteView, GradeUpdateView,
                                             create_grades_in_bulk_view)

app_name = "grades"

urlpatterns = [
    path(
        "<slug:class_slug>/<slug:subject_slug>/add/",
        GradeCreateView.as_view(),
        name="add",
    ),
    path("update/<int:pk>/", GradeUpdateView.as_view(), name="update"),
    path("delete/<int:pk>/", GradeDeleteView.as_view(), name="delete"),
    path(
        "<slug:class_slug>/<slug:subject_slug>/",
        ClassGradesView.as_view(),
        name="class_grades",
    ),
    path(
        "<slug:class_slug>/<slug:subject_slug>/add_in_bulk/",
        create_grades_in_bulk_view,
        name="create_grades_in_bulk",
    ),
]
