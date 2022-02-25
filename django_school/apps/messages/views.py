from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from django_school.apps.classes.models import Class
from django_school.apps.messages.forms import MessageForm
from django_school.apps.messages.models import Message

User = get_user_model()


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    ordering = ["-created"]
    paginate_by = 10
    context_object_name = "school_messages"

    def get_queryset(self):
        return super().get_queryset().select_related("sender")


class ReceivedMessageListView(MessageListView):
    template_name = "messages/received_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .received(self.request.user)
            .with_statuses(receiver=self.request.user)
        )


class SentMessageListView(MessageListView):
    template_name = "messages/sent_list.html"

    def get_queryset(self):
        return super().get_queryset().sent(self.request.user)


class MessageCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("messages:sent")
    success_message = "The message has been sent successfully"
    template_name = "messages/message_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["sender"] = self.request.user

        return kwargs

    def get_initial(self):
        message_pk = self.request.GET.get("reply_to", None)
        if not message_pk:
            return

        messages_qs = Message.objects.received(self.request.user)
        message_to_response = get_object_or_404(messages_qs, pk=message_pk)

        reply_content = "\n".join(
            [f"> {line}" for line in message_to_response.content.split("\n")]
        )

        return {
            "receivers": [message_to_response.sender_id],
            "topic": f"RE: {message_to_response.topic}",
            "content": f"\n\n{reply_content}",
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teachers = User.teachers.all()
        classes = Class.objects.prefetch_related("students__parent")

        context.update(
            {
                "teachers": teachers,
                "classes": classes,
            }
        )

        return context


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    pk_url_kwarg = "message_pk"
    template_name = "messages/message_detail.html"
    context_object_name = "school_message"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(Q(sender=self.request.user) | Q(receivers=self.request.user))
            .select_related("sender")
            .with_statuses(receiver=self.request.user)
            .distinct()
        )

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)

        if self.object.status:
            status = self.object.status[0]
            if not status.is_read:
                status.is_read = True
                status.save()

        return result
