from django.core.exceptions import ValidationError
from django.test import TestCase

from django_school.apps.grades.models import Grade
from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin


class TestGradeModel(UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase):
    def test_clean_raises_ValidationError_if_grade_with_same_student_and_category_already_exists(
        self,
    ):
        student = self.create_user()
        teacher = self.create_teacher(username="teacher")
        school_class = self.create_class()
        subject = self.create_subject()
        category = self.create_grade_category(subject, school_class)
        grade = self.create_grade(category, subject, student, teacher)

        with self.assertRaises(ValidationError):
            grade = Grade(
                grade=1.0,
                weight=1,
                category=category,
                subject=subject,
                student=student,
                teacher=teacher,
            )
            grade.clean()
