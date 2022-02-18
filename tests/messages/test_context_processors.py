from django.test import RequestFactory, TestCase

from django_school.apps.messages.context_processors import \
    unread_messages_count
from django_school.apps.messages.models import MessageStatus
from tests.utils import MessagesMixin, UsersMixin


class UnreadMessagesCountTestCase(UsersMixin, MessagesMixin, TestCase):
    def test_returns_unread_messages_count(self):
        sender = self.create_teacher()
        receiver1 = self.create_student()
        for _ in range(5):
            self.create_message(sender, [receiver1])

        statuses = MessageStatus.objects.filter(receiver=receiver1)[:2]
        for status in statuses:
            status.is_read = True
            status.save()

        request = RequestFactory().get("/test")
        request.user = receiver1
        result = unread_messages_count(request)

        self.assertEqual(result, {"unread_messages_count": 3})
