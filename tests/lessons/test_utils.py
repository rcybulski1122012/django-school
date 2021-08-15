from django.test import TestCase

from django_school.apps.lessons.models import ExactLesson, Presence
from django_school.apps.lessons.utils import generate_exact_lesson
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class TestGenerateExactLesson(LessonsMixin, ClassesMixin, UsersMixin, TestCase):
    def test_creates_exact_lesson_and_presences(self):
        subject = self.create_subject()
        user = self.create_user()
        school_class = self.create_class()
        lesson = self.create_lesson(subject, user, school_class)
        students = [
            self.create_user(username=f"username{i}", school_class=school_class)
            for i in range(5)
        ]

        generate_exact_lesson(lesson)

        students_with_presence_object = [p.student for p in Presence.objects.all()]
        self.assertEqual(ExactLesson.objects.first().lesson, lesson)
        self.assertEqual(students_with_presence_object, students)
