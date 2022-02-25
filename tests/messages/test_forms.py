from django.test import TestCase

from django_school.apps.messages.forms import MessageForm
from django_school.apps.messages.models import MessageStatus
from tests.utils import MessagesMixin, UsersMixin


class MessageFormTestCase(UsersMixin, MessagesMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sender = cls.create_user(username="sender")
        cls.receiver = cls.create_user(username="receiver")
        cls.form = MessageForm(cls.get_example_form_data(), sender=cls.sender)

    @classmethod
    def get_example_form_data(cls):
        return {
            "receivers": [cls.receiver.pk],
            "topic": "Hi!",
            "content": "???",
        }

    def test_assigns_sender_to_form(self):
        self.assertEqual(self.form.sender, self.sender)

    def test_save_creates_statuses_if_commit_equals_True(self):
        self.form.save(commit=True)

        self.assertTrue(MessageStatus.objects.exists())

    def test_save_does_not_create_statuses_if_commit_equals_False(self):
        self.form.save(commit=False)

        self.assertFalse(MessageStatus.objects.exists())
