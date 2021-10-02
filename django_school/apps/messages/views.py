from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from django_school.apps.messages.models import Message


class ReceivedMessagesListView(LoginRequiredMixin, ListView):
    model = Message
    ordering = ["-created"]
    paginate_by = 10
    template_name = "messages/received_list.html"
    context_object_name = "school_messages"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(receivers=self.request.user)
            .select_related("sender")
            .with_statuses(receiver=self.request.user)
        )
