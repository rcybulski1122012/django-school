from django.test import TestCase
from django.urls import reverse

from tests.utils import (ClassesMixin, ResourceViewMixin, TeacherViewMixin,
                         UsersMixin)


class TestClassesListView(TeacherViewMixin, UsersMixin, ClassesMixin, TestCase):
    path_name = "classes:list"

    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_user(username="student123")

    def get_url(self):
        return reverse(self.path_name)

    def test_context_contains_list_of_classes_ordered_by_number(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(
            response.context["school_classes"], [self.school_class]
        )

    def test_displays_appropriate_message_when_there_are_no_classes(self):
        self.login(self.teacher)
        self.school_class.delete()

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(response.context["school_classes"], [])
        self.assertContains(response, "No classes have been created yet.")

    def test_renders_links_to_class_detail_view_and_timetable_view(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertContains(
            response, reverse("classes:detail", args=[self.school_class.slug])
        )
        self.assertContains(
            response, reverse("lessons:class_timetable", args=[self.school_class.slug])
        )


class TestClassDetailView(
    TeacherViewMixin, ResourceViewMixin, UsersMixin, ClassesMixin, TestCase
):
    path_name = "classes:detail"

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

    def get_url(self, class_slug=None):
        class_slug = class_slug or self.school_class.slug

        return reverse(self.path_name, args=[class_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(class_slug="slug")

    def test_context_contains_school_class(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertEqual(response.context["school_class"], self.school_class)

    def test_renders_class_info(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.school_class.number)
        self.assertContains(response, self.teacher.full_name)

    def test_renders_users_list(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.student.full_name)
        self.assertContains(response, self.student.get_absolute_url())
