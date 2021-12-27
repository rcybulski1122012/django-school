from django.core.exceptions import ValidationError
from django.test import TestCase

from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin


class GradeModelTestCase(UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(school_class=self.school_class)
        self.subject = self.create_subject()
        self.category = self.create_grade_category(self.subject, self.school_class)
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)

    def test_clean_raises_ValidationError_if_grade_with_same_student_and_category_already_exists(
        self,
    ):
        self.create_grade(self.category, self.subject, self.student, self.teacher)

        with self.assertRaises(ValidationError):
            self.create_grade(
                self.category, self.subject, self.student, self.teacher
            ).clean()

    def test_clean_raises_ValidationError_if_teacher_is_not_a_teacher(self):
        student2 = self.create_student(username="student2")

        with self.assertRaises(ValidationError):
            self.create_grade(
                self.category, self.subject, self.student, student2
            ).clean()

    def test_clean_raises_ValidationError_if_student_is_a_teacher(self):
        teacher2 = self.create_teacher(username="teacher2")

        with self.assertRaises(ValidationError):
            self.create_grade(
                self.category, self.subject, teacher2, self.teacher
            ).clean()

    def test_clean_raises_ValidationError_if_student_is_not_learning_the_subject(self):
        subject2 = self.create_subject(name="subject2")
        category2 = self.create_grade_category(subject2, self.school_class)

        with self.assertRaises(ValidationError):
            self.create_grade(category2, subject2, self.student, self.teacher).clean()

    def test_clean_raises_ValidationError_if_category_is_not_a_category_of_the_subject(
        self,
    ):
        subject2 = self.create_subject(name="subject2")
        category2 = self.create_grade_category(subject2, self.school_class)
        with self.assertRaises(ValidationError):
            self.create_grade(
                category2, self.subject, self.student, self.teacher
            ).clean()
