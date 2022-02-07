from django.urls import path

from django_school.apps.events.views import (EventCreateView, EventDeleteView,
                                             EventsCalendarView,
                                             EventUpdateView)

app_name = "events"

urlpatterns = [
    path("", EventsCalendarView.as_view(), name="calendar"),
    path("create/", EventCreateView.as_view(), name="create"),
    path("update/<int:event_pk>/", EventUpdateView.as_view(), name="update"),
    path("delete/<int:event_pk>/", EventDeleteView.as_view(), name="delete"),
]
