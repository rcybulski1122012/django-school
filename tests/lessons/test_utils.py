from django.test import TestCase

from django_school.apps.lessons.models import Attendance, LessonSession
from django_school.apps.lessons.utils import create_lesson_session
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class CreateLessonSessionTestCase(LessonsMixin, ClassesMixin, UsersMixin, TestCase):
    def test_creates_lesson_session_and_attendances(self):
        subject = self.create_subject()
        user = self.create_user()
        school_class = self.create_class()
        lesson = self.create_lesson(subject, user, school_class)
        students = [
            self.create_user(
                username=f"username{i}",
                first_name=f"firstname{i}",
                school_class=school_class,
            )
            for i in range(5)
        ]

        create_lesson_session(lesson)

        students_with_attendances = [p.student for p in Attendance.objects.all()]
        self.assertEqual(LessonSession.objects.first().lesson, lesson)
        self.assertQuerysetEqual(students_with_attendances, students, ordered=False)
