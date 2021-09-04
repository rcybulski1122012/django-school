from django.test import TestCase

from django_school.apps.grades.forms import GradeForm
from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin


class TestGradeForm(UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_user(
            username="student", school_class=self.school_class
        )
        self.subject = self.create_subject()
        self.grade_category = self.create_grade_category(
            self.subject, self.school_class
        )

    def test_student_queryset(self):
        school_class2 = self.create_class(number="2c")
        self.create_user(username="student2", school_class=school_class2)

        form = GradeForm(school_class=self.school_class, subject=self.subject)

        student_qs = form.fields["student"].queryset
        self.assertQuerysetEqual(student_qs, [self.student])

    def test_category_queryset(self):
        subject2 = self.create_subject(name="subject2")
        school_class2 = self.create_class(number="2c")
        self.create_grade_category(self.subject, school_class2)
        self.create_grade_category(subject2, self.school_class)

        form = GradeForm(school_class=self.school_class, subject=self.subject)

        categories_qs = form.fields["category"].queryset
        self.assertQuerysetEqual(categories_qs, [self.grade_category])
