from django.test import TestCase

from django_school.apps.messages.models import Message, MessageStatus
from tests.utils import MessagesMixin, UsersMixin


class MessagesQuerySetTestCase(UsersMixin, MessagesMixin, TestCase):
    def setUp(self):
        self.sender = self.create_user(username="sender")
        self.receiver = self.create_user(username="receiver")

        self.message = self.create_message(self.sender, [self.receiver])

    def test_selects_statuses_of_receivers(self):
        message = Message.objects.with_statuses(receiver=self.receiver).get()
        status = MessageStatus.objects.get()

        self.assertEqual(message.status, [status])


class MessageStatusManagerTestCase(UsersMixin, MessagesMixin, TestCase):
    def setUp(self):
        self.sender = self.create_user(username="sender")
        self.receiver = self.create_user(username="receiver")

        self.message = Message.objects.create(
            title="title", content="content", sender=self.sender
        )

    def test_create_multiple(self):
        MessageStatus.objects.create_multiple(
            message=self.message, receivers=[self.receiver]
        )

        self.assertTrue(MessageStatus.objects.exists())
