from django.test import TestCase
from django.urls import reverse

from tests.utils import ClassesMixin, CommonMixin, UsersMixin


class TestUserDetailView(ClassesMixin, UsersMixin, CommonMixin, TestCase):
    fixtures = ["groups.json"]

    def test_redirects_when_user_is_not_logged_in(self):
        user = self.create_user(username="TestDetailView")
        self.assertRedirectsWhenNotLoggedIn(reverse("users:detail", args=[user.pk]))

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        not_teacher = self.create_user()
        self.login(not_teacher)

        second_user = self.create_user(username="SecondUser")
        response = self.client.get(reverse("users:detail", args=[second_user.pk]))

        self.assertEqual(response.status_code, 403)

    def test_context_contains_user(self):
        teacher = self.create_teacher()
        self.login(teacher)
        student = self.create_user(username="Student")

        response = self.client.get(reverse("users:detail", args=[student.pk]))

        self.assertEqual(response.context["user"], student)

    def test_renders_user_information(self):
        teacher = self.create_teacher()
        self.login(teacher)
        school_class = self.create_class(number="TestClassNumber", tutor=teacher)
        address = self.create_address()

        student = self.create_user(
            username="Student",
            school_class=school_class,
            phone_number="TestNumber",
            email="TestEmailAddr@gmail.com",
            address=address,
            first_name="TestFirst",
            last_name="TestLast",
        )

        response = self.client.get(reverse("users:detail", args=[student.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContainsFew(
            response,
            school_class.number,
            "TestNumber",
            "TestEmailAddr@gmail.com",
            student.full_name,
            str(address),
        )

    def test_perform_only_6_queries(self):
        teacher = self.create_teacher()
        self.login(teacher)
        school_class = self.create_class(number="TestClassNumber", tutor=teacher)
        address = self.create_address()

        student = self.create_user(
            username="Student", school_class=school_class, address=address
        )

        with self.assertNumQueries(6):
            self.client.get(reverse("users:detail", args=[student.pk]))
