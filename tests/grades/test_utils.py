from django.test import TestCase

from django_school.apps.grades.utils import \
    does_the_teacher_teach_the_subject_to_the_class
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class DoesTheTeacherTeachTheSubjectToTheClassTestCase(
    UsersMixin, ClassesMixin, LessonsMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.subject = self.create_subject()

    def test_if_teacher_teaches(self):
        self.create_lesson(self.subject, self.teacher, self.school_class)

        result = does_the_teacher_teach_the_subject_to_the_class(
            self.teacher, self.subject, self.school_class
        )

        self.assertTrue(result)

    def test_if_teacher_does_not_teach(self):
        result = does_the_teacher_teach_the_subject_to_the_class(
            self.teacher, self.subject, self.school_class
        )

        self.assertFalse(result)
