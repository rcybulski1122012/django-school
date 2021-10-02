from django.urls import path

from django_school.apps.messages.views import ReceivedMessagesListView

app_name = "messages"

urlpatterns = [
    path("received/", ReceivedMessagesListView.as_view(), name="received"),
]
