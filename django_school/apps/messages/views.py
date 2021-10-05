from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from django_school.apps.classes.models import Class
from django_school.apps.messages.forms import MessageForm
from django_school.apps.messages.models import Message

User = get_user_model()


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


# TODO: test it
class MessageCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "messages/message_form.html"
    success_url = reverse_lazy("messages:sent")
    success_message = "The message has been sent successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teachers = User.teachers.all()
        classes = Class.objects.prefetch_related("students")

        context.update(
            {
                "teachers": teachers,
                "classes": classes,
            }
        )

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["sender"] = self.request.user

        return kwargs
