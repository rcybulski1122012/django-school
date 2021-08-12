import datetime

from django.core.management import call_command
from django.test import TestCase

from django_school.apps.lessons.models import ExactLesson, Presence
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class DateMock(datetime.date):
    @classmethod
    def today(cls):
        return cls(year=2021, month=1, day=1)


datetime.date = DateMock


class TestGenerateExactLessons(LessonsMixin, UsersMixin, ClassesMixin, TestCase):
    def setUp(self):
        self.subject = self.create_subject()
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_user(
            username="Student123", school_class=self.school_class
        )

    def test_creates_exact_lessons_for_today_and_presences(self):
        friday_lesson = self.create_lesson(
            self.subject, self.teacher, self.school_class, weekday="fri"
        )
        self.create_lesson(self.subject, self.teacher, self.school_class, weekday="mon")

        call_command("generate_exact_lessons")

        exact_lesson = ExactLesson.objects.all()[0]
        presence = Presence.objects.get(exact_lesson=exact_lesson)
        self.assertEqual(exact_lesson.lesson, friday_lesson)
        self.assertEqual(presence.student, self.student)
        self.assertEqual(presence.exact_lesson, exact_lesson)
        self.assertEqual(presence.status, "none")

    def test_performs_optimal_number_of_queries(self):
        student2 = self.create_user(
            username="Student321", school_class=self.school_class
        )
        lessons = [
            self.create_lesson(
                self.subject, self.teacher, self.school_class, weekday="fri"
            )
            for _ in range(5)
        ]

        with self.assertNumQueries(12):
            call_command("generate_exact_lessons")
