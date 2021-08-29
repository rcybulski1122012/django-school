from django.test import TestCase
from django.urls import reverse

from django_school.apps.users.views import (SUCCESS_PASSWORD_CHANGE_MESSAGE,
                                            SUCCESS_PROFILE_UPDATE_MESSAGE)
from tests.utils import ClassesMixin, CommonMixin, UsersMixin


class TestUserDetailView(UsersMixin, ClassesMixin, CommonMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class(tutor=self.teacher)
        self.address = self.create_address()
        self.student = self.create_user(
            username="Student",
            school_class=self.school_class,
            phone_number="TestNumber",
            email="TestEmailAddr@gmail.com",
            address=self.address,
            first_name="TestFirst",
            last_name="TestLast",
        )

    def test_redirects_when_user_is_not_logged_in(self):
        self.assertRedirectsWhenNotLoggedIn(
            reverse("users:detail", args=[self.student.slug])
        )

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        self.login(self.student)

        response = self.client.get(reverse("users:detail", args=[self.student.slug]))

        self.assertEqual(response.status_code, 403)

    def test_returns_200_when_user_is_in_teachers_group(self):
        self.login(self.teacher)

        response = self.client.get(reverse("users:detail", args=[self.student.slug]))

        self.assertEqual(response.status_code, 200)

    def test_returns_404_when_user_does_not_exist(self):
        self.login(self.teacher)

        response = self.client.get(reverse("users:detail", args=["slug"]))

        self.assertEqual(response.status_code, 404)

    def test_context_contains_user(self):
        self.login(self.teacher)

        response = self.client.get(reverse("users:detail", args=[self.student.slug]))

        self.assertEqual(response.context["user"], self.student)

    def test_renders_user_information(self):
        self.login(self.teacher)

        response = self.client.get(reverse("users:detail", args=[self.student.slug]))

        self.assertContainsFew(
            response,
            self.school_class.number,
            "TestNumber",
            "TestEmailAddr@gmail.com",
            self.student.full_name,
            str(self.address),
        )


class TestProfileView(UsersMixin, CommonMixin, TestCase):
    def setUp(self):
        self.address = self.create_address()
        self.student = self.create_user(address=self.address)

    def test_redirects_when_user_is_not_logged_in(self):
        self.assertRedirectsWhenNotLoggedIn(reverse("users:profile"))

    def test_context_contains_user_info_and_address_form(self):
        self.login(self.student)

        response = self.client.get(reverse("users:profile"))

        self.assertIn("user_info_form", response.context)
        self.assertIn("address_form", response.context)

    def test_updates_profile_and_displays_success_message_when_data_is_correct(self):
        self.login(self.student)
        user_data = {
            "phone_number": "333-444-555",
            "email": "new@email.com",
        }
        address_data = {
            "street": "new-street",
            "building_number": "5",
            "apartment_number": "10",
            "city": "new-city",
            "zip_code": "new-code",
            "country": "new-country",
        }
        response = self.client.post(
            reverse("users:profile"), {**user_data, **address_data}, follow=True
        )
        self.student.refresh_from_db()
        self.address.refresh_from_db()

        self.assertModelFieldsEqual(self.student, **user_data)
        self.assertModelFieldsEqual(self.address, **address_data)
        self.assertContains(response, SUCCESS_PROFILE_UPDATE_MESSAGE)

    def test_displays_error_message_when_data_is_incorrect(self):
        self.login(self.student)

        response = self.client.post(reverse("users:profile"), {"incorrect": "data"})

        self.assertContains(response, "This field is required")


class TestPasswordChangeWithMessageView(UsersMixin, TestCase):
    def setUp(self):
        self.user = self.create_user()

    def test_redirects_when_user_is_not_logged_in(self):
        self.assertRedirectsWhenNotLoggedIn(reverse("users:password_change"))

    def test_redirects_to_profile(self):
        self.login(self.user)
        data = {
            "old_password": self.DEFAULT_PASSWORD,
            "new_password1": "NewPassword1!",
            "new_password2": "NewPassword1!",
        }

        response = self.client.post(reverse("users:password_change"), data)

        self.assertRedirects(response, reverse("users:profile"))

    def test_displays_success_message(self):
        self.login(self.user)
        data = {
            "old_password": self.DEFAULT_PASSWORD,
            "new_password1": "NewPassword1!",
            "new_password2": "NewPassword1!",
        }

        response = self.client.post(reverse("users:password_change"), data, follow=True)

        self.assertContains(response, SUCCESS_PASSWORD_CHANGE_MESSAGE)
