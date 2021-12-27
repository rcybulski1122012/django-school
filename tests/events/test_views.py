import datetime

from django.test import TestCase
from django.urls import reverse

from tests.utils import ClassesMixin, EventsMixin, LoginRequiredTestMixin, UsersMixin


class EventsCalendarViewTestCase(
    LoginRequiredTestMixin, UsersMixin, ClassesMixin, EventsMixin, TestCase
):
    path_name = "events:calendar"

    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(school_class=self.school_class)
        self.current_month_date = datetime.date.today()
        self.next_month_date = datetime.date.today() + datetime.timedelta(days=30)
        self.current_month_event = self.create_event(
            self.teacher, self.school_class, self.current_month_date, "Current month"
        )
        self.next_month_event = self.create_event(
            self.teacher, self.school_class, self.next_month_date, "Next month"
        )

    def get_url(self, date=None):
        result = reverse(self.path_name)

        if date:
            year, month = date.year, date.month
            result += f"?year={year}&month={month}"

        return result

    def test_renders_events_for_current_month_by_default(self):
        self.login(self.teacher)
        response = self.client.get(self.get_url())

        self.assertContains(response, self.current_month_event.title)
        self.assertNotContains(response, self.next_month_event.title)

    def test_renders_events_for_given_month(self):
        self.login(self.teacher)
        response = self.client.get(self.get_url(date=self.next_month_date))

        self.assertContains(response, self.next_month_event.title)
        self.assertNotContains(response, self.current_month_event.title)

    def test_renders_buttons_for_next_and_previous_month(self):
        self.login(self.teacher)
        response = self.client.get(self.get_url())

        if self.current_month_date.month != 12:
            self.assertContains(
                response,
                self.get_url(
                    date=self.current_month_date + datetime.timedelta(days=30)
                ),
            )
        else:
            self.assertContains(
                response,
                self.get_url() + f"?year={self.current_month_date.year}&month={13}",
            )
        self.assertContains(
            response,
            self.get_url(date=self.current_month_date + datetime.timedelta(days=-30)),
        )

    def test_context_contains_year_and_month(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url(date=self.current_month_date))

        self.assertEqual(response.context["year"], self.current_month_date.year)
        self.assertEqual(response.context["month"], self.current_month_date.month)

    def test_renders_global_events_if_user_is_neither_a_teacher_nor_a_student(self):
        user = self.create_user()
        global_event = self.create_event(
            self.teacher, None, self.current_month_date, "Global Event"
        )
        self.login(user)

        response = self.client.get(self.get_url())

        self.assertContains(response, global_event.title)

    def test_renders_events_created_by_user_if_he_is_a_teacher(self):
        teacher2 = self.create_teacher(username="teacher2")
        teacher2_event = self.create_event(
            teacher2, self.school_class, self.current_month_date, "teacher2 event"
        )
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.current_month_event.title)
        self.assertNotContains(response, teacher2_event.title)

    def test_renders_class_events_if_user_is_a_student(self):
        school_class2 = self.create_class(number="2b")
        school_class2_event = self.create_event(
            self.teacher, school_class2, self.current_month_date, "school_class 2 event"
        )
        self.login(self.student)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.current_month_event.title)
        self.assertNotContains(response, school_class2_event.title)
