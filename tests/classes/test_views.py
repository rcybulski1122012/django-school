from django.test import TestCase
from django.urls import reverse

from tests.utils import ClassesMixin, CommonMixin, UsersMixin


class TestClassesListView(ClassesMixin, UsersMixin, TestCase):
    def test_redirects_when_user_is_not_logged_in(self):
        self.assertRedirectsWhenNotLoggedIn(reverse("classes:list"))

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        not_teacher = self.create_user()
        self.login(not_teacher)

        response = self.client.get(reverse("classes:list"))

        self.assertEqual(response.status_code, 403)

    def test_context_contains_list_of_classes_ordered_by_number(self):
        teacher = self.create_teacher()
        self.login(teacher)
        classes = [self.create_class(number=str(i)) for i in range(5)]

        response = self.client.get(reverse("classes:list"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["school_classes"], classes)

    def test_displays_appropriate_message_when_there_are_no_classes(self):
        teacher = self.create_teacher()
        self.login(teacher)

        response = self.client.get(reverse("classes:list"))

        self.assertQuerysetEqual(response.context["school_classes"], [])
        self.assertContains(response, "No classes have been created yet.")


class TestClassDetailView(ClassesMixin, UsersMixin, CommonMixin, TestCase):
    def test_redirects_when_user_is_not_logged_in1(self):
        school_class = self.create_class()

        self.assertRedirectsWhenNotLoggedIn(
            reverse("classes:detail", args=[school_class.pk])
        )

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        not_teacher = self.create_user()
        self.login(not_teacher)
        school_class = self.create_class()

        response = self.client.get(reverse("classes:detail", args=[school_class.pk]))

        self.assertEqual(response.status_code, 403)

    def test_returns_404_when_class_does_not_exist(self):
        teacher = self.create_teacher()
        self.login(teacher)

        response = self.client.get(reverse("classes:detail", args=[100]))

        self.assertEqual(response.status_code, 404)

    def test_context_contains_school_class(self):
        teacher = self.create_teacher()
        self.login(teacher)
        school_class = self.create_class(number="TestClassNumber", tutor=teacher)

        response = self.client.get(reverse("classes:detail", args=[school_class.pk]))

        self.assertEqual(response.context["school_class"], school_class)

    def test_renders_class_info(self):
        teacher = self.create_teacher(first_name="TestClass", last_name="TestTutor")
        self.login(teacher)
        school_class = self.create_class(number="TestClassNumber", tutor=teacher)

        response = self.client.get(reverse("classes:detail", args=[school_class.pk]))

        self.assertContainsFew(response, school_class.number, teacher.full_name)

    def test_renders_users_list(self):
        teacher = self.create_teacher(first_name="TestClass", last_name="TestTutor")
        self.login(teacher)
        school_class = self.create_class(number="TestClassNumber", tutor=teacher)
        student = self.create_user(
            username="TestStudent123",
            first_name="Student",
            last_name="ForTesting",
            school_class=school_class,
        )

        response = self.client.get(reverse("classes:detail", args=[school_class.pk]))

        self.assertContains(response, student.full_name)

    def test_performs_optimal_number_of_queries(self):
        teacher = self.create_teacher()
        self.login(teacher)
        school_class = self.create_class(number="TestClassNumber", tutor=teacher)

        with self.assertNumQueries(7):
            self.client.get(reverse("classes:detail", args=[school_class.pk]))
