from django.urls import path

from django_school.apps.messages.views import (MessageCreateView,
                                               ReceivedMessagesListView,
                                               SentMessagesListView)

app_name = "messages"

urlpatterns = [
    path("received/", ReceivedMessagesListView.as_view(), name="received"),
    path("sent/", SentMessagesListView.as_view(), name="sent"),
    path("send/", MessageCreateView.as_view(), name="send"),
]
