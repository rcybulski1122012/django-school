from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from django_school.apps.messages.context_processors import \
    unread_messages_count
from django_school.apps.messages.models import MessageStatus
from tests.utils import MessagesMixin, UsersMixin


class UnreadMessagesCountTestCase(UsersMixin, MessagesMixin, TestCase):
    def setUp(self):
        self.sender = self.create_teacher()
        self.receiver = self.create_student()
        for _ in range(5):
            self.create_message(self.sender, [self.receiver])

    def test_returns_empty_dict_if_user_is_not_authenticated(self):
        request = RequestFactory().get("/test")
        request.user = AnonymousUser()
        result = unread_messages_count(request)

        self.assertEqual(result, {})

    def test_returns_unread_messages_count_if_user_is_authenticated(self):
        statuses = MessageStatus.objects.filter(receiver=self.receiver)[:2]
        for status in statuses:
            status.is_read = True
            status.save()

        request = RequestFactory().get("/test")
        request.user = self.receiver
        result = unread_messages_count(request)

        self.assertEqual(result, {"unread_messages_count": 3})
