from django.test import TestCase

from django_school.apps.messages.models import Message, MessageStatus
from tests.utils import MessagesMixin, UsersMixin


class MessagesQuerySetTestCase(UsersMixin, MessagesMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sender = cls.create_user(username="sender")
        cls.receiver = cls.create_user(username="receiver")

        cls.message = cls.create_message(cls.sender, [cls.receiver])

    def test_with_statuses(self):
        message = Message.objects.with_statuses(receiver=self.receiver).get()
        status = MessageStatus.objects.get()

        self.assertEqual(message.status, [status])


class MessageStatusManagerTestCase(UsersMixin, MessagesMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sender = cls.create_user(username="sender")
        cls.receiver = cls.create_user(username="receiver")

        cls.message = Message.objects.create(
            topic="topic", content="content", sender=cls.sender
        )

    def test_create_multiple(self):
        MessageStatus.objects.create_multiple(
            message=self.message, receivers=[self.receiver]
        )

        self.assertTrue(MessageStatus.objects.exists())
