from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from django_school.apps.messages.models import Message


class MessagesListView(LoginRequiredMixin, ListView):
    model = Message
    ordering = ["-created"]
    paginate_by = 10
    context_object_name = "school_messages"

    def get_queryset(self):
        return super().get_queryset().select_related("sender")


class ReceivedMessagesListView(MessagesListView):
    template_name = "messages/received_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(receivers=self.request.user)
            .with_statuses(receiver=self.request.user)
        )


class SentMessagesListView(MessagesListView):
    template_name = "messages/sent_list.html"

    def get_queryset(self):
        return super().get_queryset().filter(sender=self.request.user)
