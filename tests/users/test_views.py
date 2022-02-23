from django.test import TestCase
from django.urls import reverse

from tests.utils import (ClassesMixin, CommonMixin, LoginRequiredTestMixin,
                         ResourceViewTestMixin, RolesRequiredTestMixin,
                         UsersMixin)


class StudentDetailViewTestCase(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    CommonMixin,
    TestCase,
):
    path_name = "users:detail"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class(tutor=cls.teacher)
        cls.address = cls.create_address()
        cls.student = cls.create_user(
            username="Student",
            school_class=cls.school_class,
            phone_number="TestNumber",
            email="TestEmailAddr@gmail.com",
            address=cls.address,
            first_name="TestFirst",
            last_name="TestLast",
        )

    def get_url(self, user_slug=None):
        user_slug = user_slug or self.student.slug

        return reverse(self.path_name, args=[user_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(user_slug="does-not-exist")

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def test_returns_404_if_user_is_a_teacher(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url(self.teacher.slug))

        self.assertEqual(response.status_code, 404)

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


class PasswordChangeWithMessageViewTestCase(
    LoginRequiredTestMixin, UsersMixin, TestCase
):
    path_name = "users:password_change"

    @classmethod
    def setUpTestData(cls):
        cls.user = cls.create_user()

    def get_url(self):
        return reverse(self.path_name)

    def get_permitted_user(self):
        return None

    def test_redirects_to_index(self):
        self.login(self.user)
        data = {
            "old_password": self.DEFAULT_PASSWORD,
            "new_password1": "NewPassword1!",
            "new_password2": "NewPassword1!",
        }

        response = self.client.post(self.get_url(), data)

        self.assertRedirects(response, reverse("index"))

    def test_displays_success_message(self):
        self.login(self.user)
        data = {
            "old_password": self.DEFAULT_PASSWORD,
            "new_password1": "NewPassword1!",
            "new_password2": "NewPassword1!",
        }

        response = self.client.post(self.get_url(), data, follow=True)

        self.assertContains(response, "The password has been changed successfully.")
