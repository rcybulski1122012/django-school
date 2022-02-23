from datetime import date
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from django_school.apps.lessons.models import Attendance, LessonSession
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class GenerateLessonSessionTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subject = cls.create_subject()
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_user(
            username="Student123", school_class=cls.school_class
        )

    def test_creates_lesson_sessions_and_attendances_for_today(self):
        friday_lesson = self.create_lesson(
            self.subject, self.teacher, self.school_class, weekday="fri"
        )
        self.create_lesson(self.subject, self.teacher, self.school_class, weekday="mon")

        with patch(
            "django_school.apps.lessons.management.commands.create_lesson_sessions.date"
        ) as mock_date:
            mock_date.today.return_value = date(2021, 1, 1)
            call_command("create_lesson_sessions")

        lesson_session = LessonSession.objects.all()[0]
        attendance = Attendance.objects.get(lesson_session=lesson_session)
        self.assertEqual(lesson_session.lesson, friday_lesson)
        self.assertEqual(attendance.student, self.student)
        self.assertEqual(attendance.lesson_session, lesson_session)
        self.assertEqual(attendance.status, "none")

    def test_performs_optimal_number_of_queries(self):
        self.create_user(username="Student321", school_class=self.school_class)
        for _ in range(5):
            self.create_lesson(
                self.subject, self.teacher, self.school_class, weekday="fri"
            )

        with self.assertNumQueries(12):
            with patch(
                "django_school.apps.lessons.management"
                ".commands.create_lesson_sessions.date"
            ) as mock_date:
                mock_date.today.return_value = date(2021, 1, 1)
                call_command("create_lesson_sessions")
