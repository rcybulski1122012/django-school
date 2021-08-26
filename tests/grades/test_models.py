from django.core.exceptions import ValidationError
from django.test import TestCase

from django_school.apps.grades.models import Grade, GradeCategory
from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin


class TestGradeModel(UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase):
    def setUp(self):
        self.student = self.create_user()
        self.teacher = self.create_teacher(username="teacher")
        self.school_class = self.create_class()
        self.subject = self.create_subject()
        self.category = self.create_grade_category(self.subject, self.school_class)

    def test_clean_raises_ValidationError_if_grade_with_same_student_and_category_already_exists(
        self,
    ):
        grade1 = self.create_grade(
            self.category, self.subject, self.student, self.teacher
        )

        with self.assertRaises(ValidationError):
            Grade(
                grade=1.0,
                weight=1,
                category=self.category,
                subject=self.subject,
                student=self.student,
                teacher=self.teacher,
            ).clean()

    def test_clean_raises_ValidationError_if_teacher_is_not_in_teachers_group(self):
        student2 = self.create_user(username="student2")

        with self.assertRaises(ValidationError):
            Grade(
                grade=1.0,
                weight=1,
                category=self.category,
                subject=self.subject,
                student=self.student,
                teacher=student2,
            ).clean()

    def test_clean_raises_ValidationError_if_student_is_in_teachers_group(self):
        teacher2 = self.create_teacher(username="teacher2")

        with self.assertRaises(ValidationError):
            Grade(
                grade=1.0,
                weight=1,
                category=self.category,
                subject=self.subject,
                student=teacher2,
                teacher=self.teacher,
            ).clean()

    def test_clean_raises_ValidationError_if_student_is_not_learning_the_subject(self):
        subject2 = self.create_subject(name="subject2")

        with self.assertRaises(ValidationError):
            Grade(
                grade=1.0,
                weight=1,
                category=self.category,
                subject=subject2,
                student=self.student,
                teacher=self.teacher,
            ).clean()


class TestGradeCategoryModel(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    def test_clean_raises_ValidationError_if_class_is_not_learning_the_subject(self):
        school_class = self.create_class()
        subject = self.create_subject()

        with self.assertRaises(ValidationError):
            GradeCategory(
                subject=subject, school_class=school_class, name="Category"
            ).clean()
