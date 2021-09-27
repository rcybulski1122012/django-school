from django.urls import path

from django_school.apps.grades.views import (ClassGradesView,
                                             GradeCategoryDetailView,
                                             GradeCategoryFormTemplateView,
                                             GradeCategoryUpdateView,
                                             GradeCreateView, GradeDeleteView,
                                             GradeUpdateView,
                                             create_grades_in_bulk_view,
                                             grade_categories_view,
                                             grade_category_delete_view)

app_name = "grades"

urlpatterns = [
    path(
        "categories/htmx/form/",
        GradeCategoryFormTemplateView.as_view(),
        name="grade_category_form",
    ),
    path(
        "categories/htmx/<int:pk>/",
        GradeCategoryDetailView.as_view(),
        name="grade_category_detail",
    ),
    path(
        "categories/htmx/<int:pk>/delete/",
        grade_category_delete_view,
        name="grade_category_delete",
    ),
    path(
        "categories/htmx/<int:pk>/update/",
        GradeCategoryUpdateView.as_view(),
        name="grade_category_update",
    ),
    path(
        "categories/<slug:class_slug>/<slug:subject_slug>/",
        grade_categories_view,
        name="grade_categories",
    ),
    path(
        "<slug:class_slug>/<slug:subject_slug>/add/",
        GradeCreateView.as_view(),
        name="add",
    ),
    path(
        "<slug:class_slug>/<slug:subject_slug>/add_in_bulk/",
        create_grades_in_bulk_view,
        name="add_in_bulk",
    ),
    path("update/<int:grade_pk>/", GradeUpdateView.as_view(), name="update"),
    path("delete/<int:grade_pk>/", GradeDeleteView.as_view(), name="delete"),
    path(
        "<slug:class_slug>/<slug:subject_slug>/",
        ClassGradesView.as_view(),
        name="class_grades",
    ),
]
