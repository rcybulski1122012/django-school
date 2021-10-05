from django.test import TestCase
from django.urls import reverse

from django_school.apps.messages.models import Message, MessageStatus
from tests.utils import (ClassesMixin, LoginRequiredTestMixin, MessagesMixin,
                         UsersMixin)


class MessagesListViewTestMixin(LoginRequiredTestMixin, UsersMixin, MessagesMixin):
    def setUp(self):
        self.user1 = self.create_user(username="user1")
        self.user2 = self.create_user(username="user2")

        self.message1 = self.create_message(self.user1, [self.user2])
        self.message2 = self.create_message(self.user2, [self.user1])

    def get_url(self):
        return reverse(self.path_name)

    def test_renders_appropriate_message_when_there_are_no_messages(self):
        self.login(self.user1)
        self.message1.delete()
        self.message2.delete()

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(response.context["school_messages"], [])
        self.assertContains(response, "You don't have any messages.")

    def test_renders_paginator_if_more_messages_than_10(self):
        self.login(self.user1)

        response = self.client.get(self.get_url())

        self.assertNotContains(response, '<ul class="pagination">')

        for i in range(10):
            self.create_message(self.user1, [self.user2])
            self.create_message(self.user2, [self.user1])

        response = self.client.get(self.get_url())

        messages = response.context["school_messages"]
        self.assertEqual(10, messages.count())
        self.assertContains(response, '<ul class="pagination">')


class ReceivedMessagesListViewTestCase(MessagesListViewTestMixin, TestCase):
    path_name = "messages:received"

    def test_context_contains_received_messages(self):
        self.login(self.user1)

        response = self.client.get(self.get_url())

        messages = response.context["school_messages"]
        self.assertQuerysetEqual(messages, [self.message2])

    def test_renders_message_topic_and_sender_full_name(self):
        self.login(self.user1)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.message2.topic)
        self.assertContains(response, self.message2.sender.full_name)

    def test_link_has_message_unread_class_if_unread(self):
        self.login(self.user1)

        response = self.client.get(self.get_url())

        self.assertContains(response, "message-unread")

        self.message2.statuses.update(is_read=True)
        response = self.client.get(self.get_url())

        self.assertNotContains(response, "message-unread")


class SentMessagesListViewTestCase(MessagesListViewTestMixin, TestCase):
    path_name = "messages:sent"

    def test_context_contains_received_messages(self):
        self.login(self.user1)

        response = self.client.get(self.get_url())

        messages = response.context["school_messages"]
        self.assertQuerysetEqual(messages, [self.message1])


class MessageCreateViewTestCase(
    LoginRequiredTestMixin, UsersMixin, ClassesMixin, MessagesMixin, TestCase
):
    path_name = "messages:send"

    def setUp(self):
        self.sender = self.create_user(username="sender")
        self.receiver = self.create_teacher(username="receiver")

    def get_url(self):
        return reverse(self.path_name)

    def get_example_form_data(self):
        return {
            "receivers": [self.receiver.pk],
            "topic": "Hi!",
            "content": "???",
        }

    def test_creates_message_and_message_statuses(self):
        self.login(self.sender)

        self.client.post(self.get_url(), self.get_example_form_data())

        self.assertTrue(Message.objects.exists())
        self.assertTrue(MessageStatus.objects.exists())

    def test_redirects_to_sent_messages_after_successful_creation(self):
        self.login(self.sender)

        response = self.client.post(self.get_url(), self.get_example_form_data())

        self.assertRedirects(response, reverse("messages:sent"))

    def test_renders_success_message_after_successful_creation(self):
        self.login(self.sender)

        response = self.client.post(
            self.get_url(), self.get_example_form_data(), follow=True
        )

        self.assertContains(response, "The message has been sent successfully")

    def test_renders_error_when_any_receivers_are_not_chosen(self):
        self.login(self.sender)
        data = {
            "receivers": [],
            "topic": "Hi!",
            "content": "???",
        }
        response = self.client.post(self.get_url(), data)

        self.assertContains(response, "This field is required.")

    def test_renders_checkboxes_for_users(self):
        self.login(self.sender)

        response = self.client.get(self.get_url())

        print(response.content)

        self.assertContains(
            response,
            f'<input type="checkbox" name="receivers" value="{self.receiver.pk}"',
        )

    def test_context_contains_teachers_qs_and_classes_qs(self):
        school_class = self.create_class()
        self.login(self.sender)

        response = self.client.get(self.get_url())

        teachers_qs = response.context["teachers"]
        classes_qs = response.context["classes"]
        self.assertQuerysetEqual(teachers_qs, [self.receiver])
        self.assertQuerysetEqual(classes_qs, [school_class])


class MessageDetailViewTestView(
    LoginRequiredTestMixin, UsersMixin, MessagesMixin, TestCase
):
    path_name = "messages:detail"

    def setUp(self):
        self.sender = self.create_user(username="sender")
        self.receiver = self.create_user(username="receiver")
        self.user = self.create_user()

        self.message = self.create_message(self.sender, [self.receiver])

    def get_url(self, message_pk=None, **kwargs):
        if message_pk:
            return reverse(self.path_name, args=[message_pk])
        else:
            return reverse(self.path_name, args=[self.message.pk])

    def test_returns_403_when_user_is_not_sender_or_receiver_of_the_message(self):
        self.login(self.user)

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 403)

    def test_context_contains_message(self):
        self.login(self.receiver)

        response = self.client.get(self.get_url())

        self.assertEqual(response.context["school_message"], self.message)

    def test_renders_message_info(self):
        self.login(self.receiver)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.message.topic)
        self.assertContains(response, self.message.content)
        self.assertContains(response, self.sender.full_name)
        self.assertContains(response, self.receiver.full_name)

    def test_sets_status_is_read_to_True_if_not_read(self):
        self.login(self.receiver)

        self.client.get(self.get_url())

        status = MessageStatus.objects.filter(
            message=self.message, receiver=self.receiver
        ).get()
        self.assertTrue(status.is_read)
