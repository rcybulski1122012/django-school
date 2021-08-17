from django.urls import path

from django_school.apps.lessons.views import (ClassTimetableView,
                                              TeacherLessonSessionListView,
                                              TeacherTimetableView,
                                              lesson_session_detail_view,
                                              timetable_list_view)

app_name = "lessons"

urlpatterns = [
    path(
        "class_timetable/<int:pk>/",
        ClassTimetableView.as_view(),
        name="class_timetable",
    ),
    path("timetables/", timetable_list_view, name="timetables_list"),
    path(
        "teacher_timetable/<int:pk>/",
        TeacherTimetableView.as_view(),
        name="teacher_timetable",
    ),
    path(
        "sessions/",
        TeacherLessonSessionListView.as_view(),
        name="sessions",
    ),
    path(
        "sessions/<int:pk>/",
        lesson_session_detail_view,
        name="session_detail",
    ),
]
