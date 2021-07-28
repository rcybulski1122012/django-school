from django.test import TestCase
from django.urls import reverse

from django_school.apps.common.models import Address
from tests.utils import ClassesMixin, UsersMixin


class TestUserDetailView(ClassesMixin, UsersMixin, TestCase):
    fixtures = ["groups.json"]

    def test_redirects_when_user_is_not_logged_in(self):
        user = self.create_user()
        expected_url = (
            f"{reverse('users:login')}?next={reverse('users:detail', args=[user.pk])}"
        )

        response = self.client.get(reverse("users:detail", args=[user.pk]))

        self.assertRedirects(response, expected_url)

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        self.create_user()
        self.login()
        user = self.create_user(username="SecondUser")

        response = self.client.get(reverse("users:detail", args=[user.pk]))

        self.assertEqual(response.status_code, 403)

    def test_renders_user_information(self):
        user1 = self.create_user()
        self.login()
        self.add_user_to_group(user1, "teachers")
        school_class = self.create_class(number="TestClassNumber", tutor=user1)
        address = Address.objects.create(
            street="TestStreet",
            building_number=1,
            city="TestCity",
            zip_code="TestCode",
            country="TestCountry",
        )
        user_info = {
            "school_class": school_class,
            "phone_number": "TestNumber",
            "email": "TestEmailAddr@gmail.com",
            "address": address,
            "first_name": "TestFirst",
            "last_name": "TestLast",
        }
        user2 = self.create_user(username="SecondUser", **user_info)

        response = self.client.get(reverse("users:detail", args=[user2.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, school_class.number)
        self.assertContains(response, "TestNumber")
        self.assertContains(response, "TestEmailAddr@gmail.com")
        self.assertContains(response, "TestFirst TestLast")
        self.assertContains(response, str(address))

    def test_perform_only_6_queries(self):
        user1 = self.create_user()
        self.login()
        self.add_user_to_group(user1, "teachers")
        school_class = self.create_class(number="TestClassNumber", tutor=user1)

        # TODO: CommonMixin
        address = Address.objects.create(
            street="TestStreet",
            building_number=1,
            city="TestCity",
            zip_code="TestCode",
            country="TestCountry",
        )

        user2 = self.create_user(
            username="SecondUser", school_class=school_class, address=address
        )

        with self.assertNumQueries(6):
            self.client.get(reverse("users:detail", args=[user2.pk]))
