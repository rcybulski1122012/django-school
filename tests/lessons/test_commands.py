import datetime

from django.core.management import call_command
from django.test import TestCase

from django_school.apps.lessons.models import ExactLesson
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class DateMock(datetime.date):
    @classmethod
    def today(cls):
        return cls(year=2021, month=1, day=1)


datetime.date = DateMock


class TestGenerateExactLessons(LessonsMixin, UsersMixin, ClassesMixin, TestCase):
    def test_creates_exact_lessons_for_today(self):
        subject = self.create_subject()
        teacher = self.create_teacher()
        school_class = self.create_class()
        friday_lesson = self.create_lesson(
            subject, teacher, school_class, weekday="fri"
        )
        self.create_lesson(subject, teacher, school_class, weekday="mon")

        call_command("generate_exact_lessons")

        exact_lessons = ExactLesson.objects.all()
        self.assertEqual(len(exact_lessons), 1)
        self.assertEqual(exact_lessons[0].lesson, friday_lesson)
