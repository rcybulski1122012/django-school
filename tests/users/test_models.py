from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin

User = get_user_model()


class TestUserModel(UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase):
    def test_full_name(self):
        user = self.create_user(first_name="FirstName", last_name="LastName")

        self.assertEqual(user.full_name, "FirstName LastName")

    def test_slugify_on_save_if_slug_not_given(self):
        user = User.objects.create(first_name="FirstName", last_name="LastName")

        self.assertEqual(user.slug, "firstname-lastname")

    def test_does_not_slugify_if_slug_given(self):
        user = self.create_user(slug="slug")

        self.assertEqual(user.slug, "slug")

    def test_is_teacher(self):
        user = self.create_user()

        self.assertFalse(user.is_teacher)

        teachers_group = Group.objects.get(name="teachers")
        user.groups.add(teachers_group)

        self.assertTrue(user.is_teacher)
