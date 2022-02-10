from django.conf import settings
from django.db import models
from django.db.models import Prefetch
from django.urls import reverse

from martor.models import MartorField


class MessagesQuerySet(models.QuerySet):
    def with_statuses(self, receiver):
        qs = self.prefetch_related(
            Prefetch(
                "statuses",
                queryset=MessageStatus.objects.filter(receiver=receiver),
                to_attr="status",
            )
        )

        return qs


class Message(models.Model):
    topic = models.CharField(max_length=64)
    content = MartorField()

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_sent"
    )

    receivers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="MessageStatus",
        related_name="messages_received",
    )
    created = models.DateTimeField(auto_now_add=True)

    objects = MessagesQuerySet.as_manager()

    @property
    def detail_url(self):
        return reverse("messages:detail", args=[self.pk])


class MessageStatusManager(models.Manager):
    def create_multiple(self, message, receivers):
        statuses = [
            self.model(message=message, receiver=receiver) for receiver in receivers
        ]
        self.model.objects.bulk_create(statuses)

        return statuses


class MessageStatus(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="statuses"
    )
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    is_read = models.BooleanField(default=False)

    objects = MessageStatusManager()
