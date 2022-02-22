from django.urls import include, path

from django_school.apps.grades.views import (ClassGradesView,
                                             GradeCategoryDeleteView,
                                             GradeCategoryDetailView,
                                             GradeCategoryFormTemplateView,
                                             GradeCategoryUpdateView,
                                             GradeCreateView, GradeDeleteView,
                                             GradeUpdateView,
                                             StudentGradesView,
                                             create_grades_in_bulk_view,
                                             grade_categories_view)

app_name = "grades"

categories_urlpatterns = [
    path("htmx/form/", GradeCategoryFormTemplateView.as_view(), name="form"),
    path("htmx/<int:pk>/", GradeCategoryDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", GradeCategoryDeleteView.as_view(), name="delete"),
    path(
        "htmx/<int:pk>/update/",
        GradeCategoryUpdateView.as_view(),
        name="update",
    ),
    path(
        "<slug:class_slug>/<slug:subject_slug>/",
        grade_categories_view,
        name="create",
    ),
]

urlpatterns = [
    path(
        "categories/",
        include(
            (categories_urlpatterns, "categories"),
            namespace="categories",
        ),
    ),
    path(
        "student/<slug:student_slug>",
        StudentGradesView.as_view(),
        name="student_grades",
    ),
    path(
        "<slug:class_slug>/<slug:subject_slug>/add/",
        GradeCreateView.as_view(),
        name="add",
    ),
    path(
        "<int:category_pk>/add_in_bulk/",
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
