from django.test import TestCase
from django.urls import reverse

from tests.utils import (
    ClassesMixin,
    CommonMixin,
    LoginRequiredTestMixin,
    ResourceViewTestMixin,
    TeacherViewTestMixin,
    UsersMixin,
)


class StudentDetailViewTestCase(
    TeacherViewTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    CommonMixin,
    TestCase,
):
    path_name = "users:detail"

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

    def get_url(self, user_slug=None):
        user_slug = user_slug or self.student.slug

        return reverse(self.path_name, args=[user_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(user_slug="does-not-exist")

    def test_returns_404_if_user_is_a_teacher(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url(self.teacher.slug))

        self.assertEquals(response.status_code, 404)

    def test_context_contains_user(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertEqual(response.context["user"], self.student)

    def test_renders_user_information(self):
        self.login(self.teacher)

        response = self.client.get(reverse("users:detail", args=[self.student.slug]))

        self.assertContains(response, self.school_class.number)
        self.assertContains(response, "TestNumber")
        self.assertContains(response, "TestEmailAddr@gmail.com")
        self.assertContains(response, self.student.full_name)
        self.assertContains(response, str(self.address))


class ProfileViewTestCase(LoginRequiredTestMixin, UsersMixin, CommonMixin, TestCase):
    path_name = "users:profile"

    def setUp(self):
        self.address = self.create_address()
        self.student = self.create_user(address=self.address)

    def get_url(self):
        return reverse(self.path_name)

    def test_context_contains_user_info_and_address_form(self):
        self.login(self.student)

        response = self.client.get(self.get_url())

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
            self.get_url(), {**user_data, **address_data}, follow=True
        )
        self.student.refresh_from_db()
        self.address.refresh_from_db()

        self.assertTrue(user_data.items() <= self.student.__dict__.items())
        self.assertTrue(address_data.items() <= self.address.__dict__.items())
        self.assertContains(
            response, "The profile information has been updated successfully."
        )

    def test_renders_error_message_when_data_is_incorrect(self):
        self.login(self.student)

        response = self.client.post(self.get_url(), {"incorrect": "data"})

        self.assertContains(response, "This field is required")


class PasswordChangeWithMessageViewTestCase(UsersMixin, TestCase):
    path_name = "users:password_change"

    def setUp(self):
        self.user = self.create_user()

    def get_url(self):
        return reverse(self.path_name)

    def test_redirects_to_profile(self):
        self.login(self.user)
        data = {
            "old_password": self.DEFAULT_PASSWORD,
            "new_password1": "NewPassword1!",
            "new_password2": "NewPassword1!",
        }

        response = self.client.post(self.get_url(), data)

        self.assertRedirects(response, reverse("users:profile"))

    def test_displays_success_message(self):
        self.login(self.user)
        data = {
            "old_password": self.DEFAULT_PASSWORD,
            "new_password1": "NewPassword1!",
            "new_password2": "NewPassword1!",
        }

        response = self.client.post(self.get_url(), data, follow=True)

        self.assertContains(response, "The password has been changed successfully.")
