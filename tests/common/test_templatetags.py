from django.test import TestCase

from django_school.apps.common.templatetags.utils import is_in_group
from tests.utils import UsersMixin


class TestIsInGroupTemplateTag(UsersMixin, TestCase):
    fixtures = ["groups.json"]

    def test_when_user_is_in_given_group(self):
        user = self.create_user()
        self.add_user_to_group(user, "teachers")

        result = is_in_group(user, "teachers")

        self.assertTrue(result)

    def test_when_user_is_not_in_given_group(self):
        user = self.create_user()

        result = is_in_group(user, "teachers")

        self.assertFalse(result)
