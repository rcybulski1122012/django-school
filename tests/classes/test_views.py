from django.test import TestCase
from django.urls import reverse

from tests.utils import ClassesMixin, CommonMixin, UsersMixin


class TestClassesListView(UsersMixin, ClassesMixin, CommonMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.student = self.create_user(username="student123")

    def test_redirects_when_user_is_not_logged_in(self):
        self.assertRedirectsWhenNotLoggedIn(reverse("classes:list"))

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        self.login(self.student)

        response = self.client.get(reverse("classes:list"))

        self.assertEqual(response.status_code, 403)

    def test_returns_200_when_user_is_in_teachers_group(self):
        self.login(self.teacher)

        response = self.client.get(reverse("classes:list"))

        self.assertEqual(response.status_code, 200)

    def test_context_contains_list_of_classes_ordered_by_number(self):
        self.login(self.teacher)
        school_classes = [self.create_class(number=str(i)) for i in range(5)]

        response = self.client.get(reverse("classes:list"))

        self.assertQuerysetEqual(response.context["school_classes"], school_classes)

    def test_displays_appropriate_message_when_there_are_no_classes(self):
        self.login(self.teacher)

        response = self.client.get(reverse("classes:list"))

        self.assertQuerysetEqual(response.context["school_classes"], [])
        self.assertContains(response, "No classes have been created yet.")

    def test_renders_links_to_class_detail_view_and_timetable_view(self):
        self.login(self.teacher)
        school_class = self.create_class()

        response = self.client.get(reverse("classes:list"))

        self.assertContainsFew(
            response,
            reverse("classes:detail", args=[school_class.pk]),
            reverse("lessons:class_timetable", args=[school_class.pk]),
        )


class TestClassDetailView(UsersMixin, ClassesMixin, CommonMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher(
            first_name="TestClass", last_name="TestTutor"
        )
        self.school_class = self.create_class(tutor=self.teacher)
        self.student = self.create_user(
            username="TestStudent123",
            first_name="Student",
            last_name="ForTesting",
            school_class=self.school_class,
        )

    def test_redirects_when_user_is_not_logged_in(self):
        self.assertRedirectsWhenNotLoggedIn(
            reverse("classes:detail", args=[self.school_class.pk])
        )

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        self.login(self.student)

        response = self.client.get(
            reverse("classes:detail", args=[self.school_class.pk])
        )

        self.assertEqual(response.status_code, 403)

    def test_returns_200_when_user_is_in_teachers_group(self):
        self.login(self.teacher)

        response = self.client.get(
            reverse("classes:detail", args=[self.school_class.pk])
        )

        self.assertEqual(response.status_code, 200)

    def test_returns_404_when_class_does_not_exist(self):
        self.login(self.teacher)

        response = self.client.get(reverse("classes:detail", args=[100]))

        self.assertEqual(response.status_code, 404)

    def test_context_contains_school_class(self):
        self.login(self.teacher)

        response = self.client.get(
            reverse("classes:detail", args=[self.school_class.pk])
        )

        self.assertEqual(response.context["school_class"], self.school_class)

    def test_renders_class_info(self):
        self.login(self.teacher)

        response = self.client.get(
            reverse("classes:detail", args=[self.school_class.pk])
        )

        self.assertContainsFew(
            response, self.school_class.number, self.teacher.full_name
        )

    def test_renders_users_list(self):
        self.login(self.teacher)

        response = self.client.get(
            reverse("classes:detail", args=[self.school_class.pk])
        )

        self.assertContains(response, self.student.full_name)

    def test_performs_optimal_number_of_queries(self):
        self.login(self.teacher)

        with self.assertNumQueries(7):
            self.client.get(reverse("classes:detail", args=[self.school_class.pk]))
