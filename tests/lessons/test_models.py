from django.test import TestCase

from django_school.apps.lessons.models import Subject


class TestSubjectModel(TestCase):
    def test_slugify_on_save_if_slug_not_given(self):
        subject = Subject.objects.create(name="Computer Science")

        self.assertEqual(subject.slug, "computer-science")

    def test_does_not_slugify_if_slug_given(self):
        subject = Subject.objects.create(name="Computer Science", slug="cs")

        self.assertEqual(subject.slug, "cs")
