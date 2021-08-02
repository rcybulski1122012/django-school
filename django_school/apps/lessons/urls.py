from django.urls import path

from django_school.apps.lessons.views import TimetablesListView, TimetableView

app_name = "lessons"

urlpatterns = [
    path("timetable/<int:pk>/", TimetableView.as_view(), name="timetable"),
    path("timetables/", TimetablesListView.as_view(), name="timetables_list"),
]
