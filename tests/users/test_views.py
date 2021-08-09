from django.test import TestCase
from django.urls import reverse

from django_school.apps.users.views import SUCCESS_PROFILE_UPDATE_MESSAGE
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

    def test_returns_404_when_user_does_not_exist(self):
        user = self.create_teacher()
        self.login(user)

        response = self.client.get(reverse("users:detail", args=[100]))

        self.assertEqual(response.status_code, 404)

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

    def test_performs_optimal_number_of_queries(self):
        teacher = self.create_teacher()
        self.login(teacher)
        school_class = self.create_class(number="TestClassNumber", tutor=teacher)
        address = self.create_address()

        student = self.create_user(
            username="Student", school_class=school_class, address=address
        )

        with self.assertNumQueries(6):
            self.client.get(reverse("users:detail", args=[student.pk]))


class TestProfileView(UsersMixin, CommonMixin, TestCase):
    def test_redirects_when_user_is_not_logged_in(self):
        self.assertRedirectsWhenNotLoggedIn(reverse("users:profile"))

    def test_context_contains_user_info_and_address_form(self):
        user = self.create_user()
        self.login(user)

        response = self.client.get(reverse("users:profile"))

        self.assertIn("user_info_form", response.context)
        self.assertIn("address_form", response.context)

    def test_updates_profile_and_displays_success_message_when_data_is_correct(self):
        address = self.create_address()
        user = self.create_user(address=address)
        self.login(user)
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
        user.refresh_from_db()
        address.refresh_from_db()

        self.assertModelFieldsEqual(user, **user_data)
        self.assertModelFieldsEqual(address, **address_data)
        self.assertContains(response, SUCCESS_PROFILE_UPDATE_MESSAGE)

    def test_displays_error_message_when_data_is_incorrect(self):
        address = self.create_address()
        user = self.create_user(address=address)
        self.login(user)

        response = self.client.post(reverse("users:profile"), {"incorrect": "data"})

        self.assertContains(response, "This field is required")
