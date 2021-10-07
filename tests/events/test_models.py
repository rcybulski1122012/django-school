import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from tests.utils import ClassesMixin, EventsMixin, UsersMixin


class EventModelTestCase(UsersMixin, ClassesMixin, EventsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.past_date = datetime.date(2010, 1, 1)
        self.future_date = datetime.date.today() + datetime.timedelta(days=10)

    def test_clean_raises_ValidationError_if_date_is_not_in_the_future(self):
        self.create_event(self.teacher, self.school_class, self.future_date).clean()

        with self.assertRaises(ValidationError):
            self.create_event(self.teacher, self.school_class, self.past_date).clean()

    def test_is_global(self):
        global_event = self.create_event(
            teacher=self.teacher, school_class=None, date=self.future_date
        )

        self.assertTrue(global_event.is_global)

        not_global_event = self.create_event(
            self.teacher, self.school_class, self.future_date
        )

        self.assertFalse(not_global_event.is_global)
