import datetime

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from django_school.apps.events.context_processors import unseen_events_count
from django_school.apps.events.models import EventStatus
from tests.utils import EventsMixin, UsersMixin


class UnseenEventsCountTestCase(UsersMixin, EventsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.teacher2 = cls.create_teacher(username="teacher2")
        cls.date = datetime.datetime.today()
        cls.event = cls.create_event(cls.teacher, None, cls.date)
        EventStatus.objects.create_multiple(cls.event)

    def test_returns_empty_dict_if_user_is_not_authenticated(self):
        request = RequestFactory().get("/test")
        request.user = AnonymousUser()

        result = unseen_events_count(request)

        self.assertEqual(result, {})

    def test_returns_unseen_events_count_if_user_is_authenticated(self):
        request = RequestFactory().get("/test")
        request.user = self.teacher2

        result = unseen_events_count(request)

        self.assertEqual(result, {"unseen_events_count": 1})
