import datetime
from collections import defaultdict

from django.test import TestCase

from django_school.apps.events.calendar import EventCalendar
from tests.utils import ClassesMixin, EventsMixin, UsersMixin


class EventCalendarTestCase(UsersMixin, ClassesMixin, EventsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.date = datetime.date.today() + datetime.timedelta(days=1)
        self.event = self.create_event(self.teacher, self.school_class, self.date)

    def test_init_creates_date_event_dict(self):
        calendar = EventCalendar([self.event])

        self.assertIsInstance(calendar.events, defaultdict)
        self.assertEqual(calendar.events[self.date], [self.event])

    def test_formatday_if_year_and_month_are_equal_None_or_day_is_equal_0(self):
        calendar = EventCalendar([self.event])
        calendar.year, calendar.month = 2021, 10

        result = calendar.formatday(day=1, weekday=5)

        self.assertEqual(result, "<td>1</td>")

        result = calendar.formatday(day=0, weekday=1)

        self.assertEqual(result, '<td class="noday">&nbsp;</td>')

    def test_formatday_renders_template_with_events_for_given_day(self):
        calendar = EventCalendar([self.event])
        calendar.year, calendar.month = self.date.year, self.date.month

        result = calendar.formatday(self.date.day, 1)

        self.assertIn(self.event.title, result)
        self.assertIn(self.event.description, result)
        self.assertIn(self.event.teacher.full_name, result)

    def test_formatmonth_sets_year_and_month_attributes_to_class(self):
        calendar = EventCalendar([self.event])
        calendar.formatmonth(theyear=1234, themonth=1)

        self.assertEqual(calendar.year, 1234)
        self.assertEqual(calendar.month, 1)
