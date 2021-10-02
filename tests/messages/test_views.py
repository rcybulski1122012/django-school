from django.test import TestCase
from django.urls import reverse

from tests.utils import LoginRequiredTestMixin, MessagesMixin, UsersMixin


class ReceivedMessagesListViewTestCase(
    LoginRequiredTestMixin, UsersMixin, MessagesMixin, TestCase
):
    path_name = "messages:received"

    def setUp(self):
        self.user1 = self.create_user(username="user1")
        self.user2 = self.create_user(username="user2")

        self.message1 = self.create_message(self.user1, [self.user2])
        self.message2 = self.create_message(self.user2, [self.user1])

    def get_url(self):
        return reverse(self.path_name)

    def test_context_contains_received_messages(self):
        self.login(self.user1)

        response = self.client.get(self.get_url())

        messages = response.context["school_messages"]
        self.assertQuerysetEqual(messages, [self.message2])

    def test_renders_message_title_sender(self):
        self.login(self.user1)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.message2.title)
        self.assertContains(response, self.message2.sender.full_name)

    def test_link_has_message_unread_class_if_unread(self):
        self.login(self.user1)

        response = self.client.get(self.get_url())

        self.assertContains(response, "message-unread")

        self.message2.statuses.update(is_read=True)
        response = self.client.get(self.get_url())

        self.assertNotContains(response, "message-unread")

    def test_renders_appropriate_message_when_there_are_no_messages(self):
        self.login(self.user1)
        self.message2.delete()

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(response.context["school_messages"], [])
        self.assertContains(response, "You don't have any messages.")
