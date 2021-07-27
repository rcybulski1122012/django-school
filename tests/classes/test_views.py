from django.test import TestCase
from django.urls import reverse

from tests.utils import AccountsMixin, ClassesMixin


class TestClassesListView(ClassesMixin, AccountsMixin, TestCase):
    fixtures = ["groups.json"]

    def test_redirects_when_user_is_not_logged_in(self):
        expected_url = f"{reverse('accounts:login')}?next={reverse('classes:list')}"

        response = self.client.get(reverse("classes:list"))

        self.assertRedirects(response, expected_url)

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        self.create_user()
        self.login()

        response = self.client.get(reverse("classes:list"))

        self.assertEqual(response.status_code, 403)

    def test_context_contains_list_of_classes_ordered_by_number(self):
        user = self.create_user()
        self.login()
        self.add_user_to_group(user, "teachers")
        classes = [self.create_class(number=str(i)) for i in range(5)]

        response = self.client.get(reverse("classes:list"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("classes", response.context)
        self.assertQuerysetEqual(response.context["classes"], classes)

    def test_displays_appropriate_message_when_there_are_no_classes(self):
        user = self.create_user()
        self.login()
        self.add_user_to_group(user, "teachers")

        response = self.client.get(reverse("classes:list"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("classes", response.context)
        self.assertQuerysetEqual(response.context["classes"], [])
        self.assertContains(response, "No classes have been created yet.")


class TestClassDetailView(ClassesMixin, AccountsMixin, TestCase):
    fixtures = ["groups.json"]

    def test_redirects_when_user_is_not_logged_in(self):
        school_class = self.create_class()
        expected_url = f"{reverse('accounts:login')}?next={reverse('classes:detail', args=[school_class.pk])}"

        response = self.client.get(reverse("classes:detail", args=[school_class.pk]))

        self.assertRedirects(response, expected_url)

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        self.create_user()
        self.login()
        school_class = self.create_class()

        response = self.client.get(reverse("classes:detail", args=[school_class.pk]))

        self.assertEqual(response.status_code, 403)

    def test_renders_class_info(self):
        user = self.create_user(first_name="TestClass", last_name="TestTutor")
        self.login()
        self.add_user_to_group(user, "teachers")
        school_class = self.create_class(number="TestClassNumber", tutor=user)

        response = self.client.get(reverse("classes:detail", args=[school_class.pk]))

        self.assertContains(response, school_class.number)
        self.assertContains(response, f"{user.first_name} {user.last_name}")

    def test_renders_users_list(self):
        pass

    def test_perform_only_x_queries(self):
        pass
