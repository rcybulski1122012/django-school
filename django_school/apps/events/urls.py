from django.urls import path

from django_school.apps.events.views import EventDeleteView, EventsCalendarView

app_name = "events"

urlpatterns = [
    path("", EventsCalendarView.as_view(), name="calendar"),
    path("delete/<event_pk>/", EventDeleteView.as_view(), name="delete"),
]
