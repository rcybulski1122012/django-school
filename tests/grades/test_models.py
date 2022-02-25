from django.core.exceptions import ValidationError
from django.test import TestCase

from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin


class GradeModelTestCase(UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.category = cls.create_grade_category(cls.subject, cls.school_class)
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)

    def test_clean_raises_ValidationError_if_grade_with_same_student_and_category_already_exists(
        self,
    ):
        self.create_grade(self.category, self.subject, self.student, self.teacher)

        with self.assertRaises(ValidationError):
            self.create_grade(
                self.category, self.subject, self.student, self.teacher
            ).clean()

    def test_clean_raises_ValidationError_if_teacher_is_not_teacher(self):
        student2 = self.create_student(username="student2")

        with self.assertRaises(ValidationError):
            self.create_grade(
                self.category, self.subject, self.student, student2
            ).clean()

    def test_clean_raises_ValidationError_if_student_is_teacher(self):
        teacher2 = self.create_teacher(username="teacher2")

        with self.assertRaises(ValidationError):
            self.create_grade(
                self.category, self.subject, teacher2, self.teacher
            ).clean()

    def test_clean_raises_ValidationError_if_student_is_not_learning_subject(self):
        subject2 = self.create_subject(name="subject2")
        category2 = self.create_grade_category(subject2, self.school_class)

        with self.assertRaises(ValidationError):
            self.create_grade(category2, subject2, self.student, self.teacher).clean()

    def test_clean_raises_ValidationError_if_category_is_not_category_of_subject(
        self,
    ):
        subject2 = self.create_subject(name="subject2")
        category2 = self.create_grade_category(subject2, self.school_class)
        with self.assertRaises(ValidationError):
            self.create_grade(
                category2, self.subject, self.student, self.teacher
            ).clean()
