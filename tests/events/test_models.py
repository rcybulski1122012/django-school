import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from django_school.apps.events.models import Event, EventStatus
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

    def test_clean_raises_ValidationError_if_teacher_is_not_a_teacher(self):
        student = self.create_student()

        with self.assertRaises(ValidationError):
            self.create_event(student, self.school_class, self.future_date).clean()

    def test_is_global(self):
        global_event = self.create_event(
            teacher=self.teacher, school_class=None, date=self.future_date
        )

        self.assertTrue(global_event.is_global)

        not_global_event = self.create_event(
            self.teacher, self.school_class, self.future_date
        )

        self.assertFalse(not_global_event.is_global)


class EventQuerySetTestCase(UsersMixin, ClassesMixin, EventsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.date = datetime.date.today() + datetime.timedelta(days=1)
        self.event = self.create_event(self.teacher, self.school_class, self.date)

    def test_for_year_and_month(self):
        self.create_event(self.teacher, self.school_class, datetime.date(2021, 1, 1))

        result = Event.objects.for_year_and_month(self.date.year, self.date.month)

        self.assertQuerysetEqual(result, [self.event])

    def test_visible_to_user_selects_events_created_by_teacher(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.create_event(teacher2, self.school_class, self.date)

        result = Event.objects.visible_to_user(self.teacher)

        self.assertQuerysetEqual(result, [self.event])

    def test_visible_to_user_selects_events_of_student_class(self):
        student = self.create_student(school_class=self.school_class)
        school_class2 = self.create_class(number="2b")
        self.create_event(self.teacher, school_class2, self.date)

        result = Event.objects.visible_to_user(student)

        self.assertQuerysetEqual(result, [self.event])

    def test_visible_to_user_selects_global_events(self):
        global_event = self.create_event(self.teacher, None, self.date)
        student = self.create_student()

        result = Event.objects.visible_to_user(student)

        self.assertQuerysetEqual(result, [global_event])

    def test_visible_to_user_select_events_of_parent_child_class(self):
        student = self.create_student(school_class=self.school_class)
        parent = self.create_parent(child=student)

        result = Event.objects.visible_to_user(parent)

        self.assertQuerysetEqual(result, [self.event])

    def test_with_statuses(self):
        student = self.create_student(school_class=self.school_class)
        EventStatus.objects.create_multiple(self.event)
        event = Event.objects.with_statuses(student).first()
        status = EventStatus.objects.first()

        self.assertEqual(event.status, [status])


class EventStatusManagerTestCase(UsersMixin, ClassesMixin, EventsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(school_class=self.school_class)
        self.parent = self.create_parent(child=self.student)
        self.date = datetime.datetime.today()
        self.create_teacher(username="teacher2")

    def test_create_multiple_creates_statuses_for_every_user_if_school_class_not_given(
        self,
    ):
        event = self.create_event(self.teacher, None, self.date)
        EventStatus.objects.create_multiple(event)

        self.assertEqual(
            EventStatus.objects.count(), 3
        )  # student, parent and second teacher

    def test_create_multiple_creates_statuses_for_students_and_parents_if_class_given(
        self,
    ):
        event = self.create_event(self.teacher, self.school_class, self.date)
        EventStatus.objects.create_multiple(event)

        self.assertEqual(EventStatus.objects.count(), 2)
