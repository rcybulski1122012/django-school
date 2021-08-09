from django.test import TestCase

from django_school.apps.users.forms import UserInfoForm
from tests.utils import UsersMixin


class TestUserInfoForm(UsersMixin, TestCase):
    def test_invalid_form_when_invalid_email_format(self):
        form = UserInfoForm(
            data={"phone_number": "123-456-789", "email": "invalid-email-format"}
        )

        self.assertFalse(form.is_valid())

    def test_valid_form_when_blank_fields(self):
        form = UserInfoForm(data={"phone_number": "", "email": ""})

        self.assertTrue(form.is_valid())

    def test_valid_form_proper_data(self):
        form = UserInfoForm(
            data={"phone_number": "123-456-789", "email": "email@email.com"}
        )

        self.assertTrue(form.is_valid())

    def test_updates_user_when_valid_form(self):
        user = self.create_user()
        data = {"phone_number": "000-111-222", "email": "updated_email@gmail.com"}

        form = UserInfoForm(
            data=data,
            instance=user,
        )
        form.save()
        user.refresh_from_db()

        self.assertEqual(user.phone_number, data["phone_number"])
        self.assertEqual(user.email, data["email"])
