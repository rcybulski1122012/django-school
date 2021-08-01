from django.test import TestCase
from django.urls import reverse

from django_school.apps.lessons.models import LESSONS_TIMES, WEEKDAYS
from tests.utils import ClassesMixin, CommonMixin, LessonsMixin, UsersMixin


class TestTimetableView(ClassesMixin, UsersMixin, LessonsMixin, CommonMixin, TestCase):
    fixtures = ["groups.json"]

    def test_returns_404_when_class_does_not_exits(self):
        response = self.client.get(reverse("lessons:timetable", args=[100]))

        self.assertEqual(response.status_code, 404)

    def test_context_contains_school_class(self):
        school_class = self.create_class()

        response = self.client.get(reverse("lessons:timetable", args=[school_class.pk]))

        self.assertEqual(response.context["school_class"], school_class)

    def test_context_contains_weekdays_and_lessons_times(self):
        school_class = self.create_class()

        response = self.client.get(reverse("lessons:timetable", args=[school_class.pk]))

        self.assertEqual(response.context["weekdays"], WEEKDAYS)
        self.assertEqual(response.context["lessons_times"], LESSONS_TIMES)

    def test_renders_lessons(self):
        teacher = self.create_teacher()
        subject = self.create_subject()
        school_class = self.create_class()
        lesson = self.create_lesson(subject, teacher, school_class)

        response = self.client.get(reverse("lessons:timetable", args=[school_class.pk]))

        self.assertContainsFew(
            response,
            teacher.full_name,
            subject.name,
            school_class.number,
            lesson.classroom,
        )

    def test_performs_optimal_number_of_queries(self):
        teacher = self.create_teacher()
        subject = self.create_subject()
        school_class = self.create_class()
        [
            self.create_lesson(subject, teacher, school_class, time=time)
            for time in LESSONS_TIMES
        ]

        with self.assertNumQueries(4):
            self.client.get(reverse("lessons:timetable", args=[school_class.pk]))
