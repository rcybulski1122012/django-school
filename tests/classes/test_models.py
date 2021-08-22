from django.test import TestCase

from django_school.apps.classes.models import Class


class TestClassModel(TestCase):
    def test_slugify_on_save_if_slug_not_given(self):
        school_class = Class.objects.create(number="4 cm")

        self.assertEqual(school_class.slug, "4-cm")

    def test_does_not_slugify_if_slug_given(self):
        school_class = Class.objects.create(number="4cm", slug="cm4")

        self.assertEqual(school_class.slug, "cm4")
