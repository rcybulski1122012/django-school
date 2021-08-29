from django.core.exceptions import ValidationError
from django.test import TestCase

from django_school.apps.classes.models import Class
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class TestClassModel(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    def test_slugify_on_save_if_slug_not_given(self):
        school_class = self.create_class(number="4 cm")

        self.assertEqual(school_class.slug, "4-cm")

    def test_does_not_slugify_if_slug_given(self):
        school_class = self.create_class(number="4cm", slug="cm4")

        self.assertEqual(school_class.slug, "cm4")

    def test_clean_raises_ValidationError_when_tutor_is_not_in_teachers_group(
        self,
    ):
        student = self.create_user()
        with self.assertRaises(ValidationError):
            Class(number="4cm", tutor=student).clean()

    def test_with_nested_resources(self):
        teacher = self.create_teacher()
        school_class = self.create_class()
        student = self.create_user(username="student", school_class=school_class)

        with self.assertNumQueries(2):
            school_class_ = list(Class.objects.with_nested_resources())[0]

        with self.assertNumQueries(0):
            tutor = school_class_.tutor
            students = school_class_.students.all()
