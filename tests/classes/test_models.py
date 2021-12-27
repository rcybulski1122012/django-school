from django.core.exceptions import ValidationError
from django.test import TestCase

from tests.utils import ClassesMixin, UsersMixin


class ClassModelTestCase(UsersMixin, ClassesMixin, TestCase):
    def test_save_slugify_if_slug_not_given(self):
        school_class = self.create_class(number="4 cm")

        self.assertEqual(school_class.slug, "4-cm")

    def test_save_does_not_slugify_if_slug_given(self):
        school_class = self.create_class(number="4cm", slug="cm4")

        self.assertEqual(school_class.slug, "cm4")

    def test_clean_raises_ValidationError_when_tutor_is_not_a_teacher(
        self,
    ):
        student = self.create_student()
        with self.assertRaises(ValidationError):
            self.create_class(number="4cm", tutor=student).clean()
