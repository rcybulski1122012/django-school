from django.urls import path

from django_school.apps.lessons.views import (ClassSubjectListView,
                                              ClassTimetableView,
                                              TeacherLessonSessionsListView,
                                              TeacherTimetableView,
                                              lesson_session_detail_view,
                                              timetables_list_view)

app_name = "lessons"

urlpatterns = [
    path("timetables/", timetables_list_view, name="timetables_list"),
    path(
        "class_timetable/<slug:class_slug>/",
        ClassTimetableView.as_view(),
        name="class_timetable",
    ),
    path(
        "teacher_timetable/<slug:teacher_slug>/",
        TeacherTimetableView.as_view(),
        name="teacher_timetable",
    ),
    path(
        "sessions/",
        TeacherLessonSessionsListView.as_view(),
        name="session_list",
    ),
    path(
        "sessions/<int:session_pk>/",
        lesson_session_detail_view,
        name="session_detail",
    ),
    path(
        "subjects/<slug:class_slug>/",
        ClassSubjectListView.as_view(),
        name="class_subject_list",
    ),
]
