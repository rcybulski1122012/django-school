from django.urls import path

from django_school.apps.events.views import EventsCalendarView

app_name = "events"

urlpatterns = [
    path("", EventsCalendarView.as_view(), name="calendar"),
]
