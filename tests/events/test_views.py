import datetime

from django.test import TestCase
from django.urls import reverse

from django_school.apps.events.models import Event, EventStatus
from tests.utils import (AjaxRequiredTestMixin, ClassesMixin, EventsMixin,
                         LessonsMixin, LoginRequiredTestMixin,
                         ResourceViewTestMixin, RolesRequiredTestMixin,
                         UsersMixin)


class EventsCalendarViewTestCase(
    LoginRequiredTestMixin, UsersMixin, ClassesMixin, EventsMixin, TestCase
):
    path_name = "events:calendar"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.current_month_date = datetime.date.today()
        cls.next_month_date = datetime.date.today() + datetime.timedelta(days=30)
        cls.current_month_event = cls.create_event(
            cls.teacher, cls.school_class, cls.current_month_date, "Current month"
        )
        cls.next_month_event = cls.create_event(
            cls.teacher, cls.school_class, cls.next_month_date, "Next month"
        )

    def get_url(self, date=None):
        result = reverse(self.path_name)

        if date:
            year, month = date.year, date.month
            result += f"?year={year}&month={month}"

        return result

    def get_permitted_user(self):
        return None

    def test_context_contains_year_and_month(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url(date=self.current_month_date))

        self.assertEqual(response.context["year"], self.current_month_date.year)
        self.assertEqual(response.context["month"], self.current_month_date.month)

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

    def test_renders_events_created_by_user_if_user_is_teacher(self):
        teacher2 = self.create_teacher(username="teacher2")
        teacher2_event = self.create_event(
            teacher2, self.school_class, self.current_month_date, "teacher2 event"
        )
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.current_month_event.title)
        self.assertNotContains(response, teacher2_event.title)

    def test_renders_class_events_if_user_is_student(self):
        school_class2 = self.create_class(number="2b")
        school_class2_event = self.create_event(
            self.teacher, school_class2, self.current_month_date, "school_class 2 event"
        )
        self.login(self.student)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.current_month_event.title)
        self.assertNotContains(response, school_class2_event.title)


class EventCreateViewTestCase(
    RolesRequiredTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    EventsMixin,
    TestCase,
):
    path_name = "events:create"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.date = datetime.date.today() + datetime.timedelta(days=1)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)

    def get_url(self):
        return reverse(self.path_name)

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def get_example_form_data(self):
        return {
            "title": "title",
            "description": "description",
            "school_class": self.school_class.pk,
            "date": self.date.strftime("%Y-%m-%d"),
        }

    def test_creates_event_and_event_statuses(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        self.client.post(self.get_url(), data)

        self.assertTrue(Event.objects.exists())
        self.assertTrue(EventStatus.objects.exists())

    def test_redirects_to_calendar_view_after_successful_create(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data)

        self.assertRedirects(response, reverse("events:calendar"))

    def test_renders_success_message_after_successful_create(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data, follow=True)

        self.assertContains(response, "The event has been created successfully")

    def test_renders_error_message_if_date_is_in_past(self):
        self.login(self.teacher)
        data = self.get_example_form_data()
        data["date"] = "2010-01-01"

        response = self.client.post(self.get_url(), data)

        self.assertContains(response, "The date must be in the future.")


class EventUpdateViewTestCase(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    EventsMixin,
    TestCase,
):
    path_name = "events:update"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.student = cls.create_student()
        cls.school_class = cls.create_class()
        cls.date = datetime.date.today() + datetime.timedelta(days=1)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.event = cls.create_event(cls.teacher, cls.school_class, cls.date)

    def get_url(self, event_pk=None):
        event_pk = event_pk or self.event.pk

        return reverse(self.path_name, args=[event_pk])

    def get_nonexistent_resource_url(self):
        return reverse(self.path_name, args=[123456])

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def get_example_form_data(self):
        return {
            "title": "new title",
            "description": "new description",
            "school_class": self.school_class.pk,
            "date": self.date.strftime("%Y-%m-%d"),
        }

    def test_updates_event(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        self.client.post(self.get_url(), data)

        self.event.refresh_from_db()
        self.assertEqual(
            [self.event.title, self.event.description],
            [data["title"], data["description"]],
        )

    def test_redirects_to_calendar_view_after_successful_update(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data)

        self.assertRedirects(response, reverse("events:calendar"))

    def test_renders_success_message_after_successful_update(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data, follow=True)

        self.assertContains(response, "The event has been updated successfully")

    def test_returns_404_if_user_is_not_creator(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        response = self.client.post(self.get_url())

        self.assertEqual(response.status_code, 404)


class EventDeleteViewTestCase(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    AjaxRequiredTestMixin,
    UsersMixin,
    ClassesMixin,
    EventsMixin,
    TestCase,
):
    path_name = "events:delete"
    ajax_required = True

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.student = cls.create_student()
        cls.school_class = cls.create_class()
        cls.date = datetime.date.today() + datetime.timedelta(days=1)
        cls.event = cls.create_event(cls.teacher, cls.school_class, cls.date)

    def get_url(self, event_pk=None):
        event_pk = event_pk or self.event.pk

        return reverse(self.path_name, args=[event_pk])

    def get_nonexistent_resource_url(self):
        return reverse(self.path_name, args=[123456])

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def test_deletes_event(self):
        self.login(self.teacher)

        self.client.post(self.get_url())

        self.assertFalse(Event.objects.exists())

    def test_redirects_to_calendar_view_after_successful_delete(self):
        self.login(self.teacher)

        response = self.client.post(self.get_url())

        self.assertRedirects(response, reverse("events:calendar"))

    def test_renders_success_message_after_successful_delete(self):
        self.login(self.teacher)

        response = self.client.post(self.get_url(), follow=True)

        self.assertContains(response, "The event has been deleted successfully.")

    def test_returns_404_if_user_is_not_creator(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        response = self.client.post(self.get_url())

        self.assertEqual(response.status_code, 404)
