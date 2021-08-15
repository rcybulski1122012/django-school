from django.test import TestCase

from django_school.apps.lessons.models import LessonSession, Presence
from django_school.apps.lessons.utils import create_lesson_session
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class TestCreateLessonSession(LessonsMixin, ClassesMixin, UsersMixin, TestCase):
    def test_creates_lesson_session_and_presences(self):
        subject = self.create_subject()
        user = self.create_user()
        school_class = self.create_class()
        lesson = self.create_lesson(subject, user, school_class)
        students = [
            self.create_user(username=f"username{i}", school_class=school_class)
            for i in range(5)
        ]

        create_lesson_session(lesson)

        students_with_presence_object = [p.student for p in Presence.objects.all()]
        self.assertEqual(LessonSession.objects.first().lesson, lesson)
        self.assertEqual(students_with_presence_object, students)
