import datetime

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from django_school.apps.events.context_processors import unseen_events_count
from django_school.apps.events.models import EventStatus
from tests.utils import EventsMixin, UsersMixin


class UnseenEventsCountTestCase(UsersMixin, EventsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.teacher2 = self.create_teacher(username="teacher2")
        self.date = datetime.datetime.today()
        self.event = self.create_event(self.teacher, None, self.date)
        EventStatus.objects.create_multiple(self.event)

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
