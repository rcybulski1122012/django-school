from django.test import TestCase

from django_school.apps.common.templatetags.utils import is_in_group
from tests.utils import UsersMixin


class TestIsInGroupTemplateTag(UsersMixin, TestCase):
    def test_when_user_is_in_given_group(self):
        teacher = self.create_teacher()

        result = is_in_group(teacher, "teachers")

        self.assertTrue(result)

    def test_when_user_is_not_in_given_group(self):
        user = self.create_user()

        result = is_in_group(user, "teachers")

        self.assertFalse(result)
