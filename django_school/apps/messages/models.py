from django.conf import settings
from django.db import models
from martor.models import MartorField


class Message(models.Model):
    title = models.CharField(max_length=64)
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


class MessageStatus(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    is_read = models.BooleanField(default=False)
    read_datetime = models.DateTimeField(auto_now=True)
