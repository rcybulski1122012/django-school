from django.test import TestCase

from tests.utils import UsersMixin


class TestUserModel(UsersMixin, TestCase):
    def test_full_name(self):
        user = self.create_user(first_name="FirstName", last_name="LastName")

        self.assertEqual(user.full_name, "FirstName LastName")
