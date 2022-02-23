from django.test import TestCase
from django.urls import reverse

from tests.utils import (ClassesMixin, LessonsMixin, ResourceViewTestMixin,
                         RolesRequiredTestMixin, UsersMixin)


class ClassesListViewTestCase(
    RolesRequiredTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    TestCase,
):
    path_name = "classes:list"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student()
        cls.subject = cls.create_subject()
        cls.create_lesson(cls.subject, cls.teacher, cls.school_class)

    def get_url(self):
        return reverse(self.path_name)

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def test_selects_classes_taught_by_the_teacher(self):
        school_class2 = self.create_class(number="2c")
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertNotIn(school_class2, response.context["school_classes"])

    def test_context_contains_list_of_classes_ordered_by_number(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(
            response.context["school_classes"], [self.school_class]
        )

    def test_renders_appropriate_message_when_there_are_no_classes(self):
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


class ClassDetailViewTestCase(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    TestCase,
):
    path_name = "classes:detail"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher(first_name="TestClass", last_name="TestTutor")
        cls.school_class = cls.create_class(tutor=cls.teacher)
        cls.student = cls.create_student(
            username="TestStudent123",
            first_name="Student",
            last_name="ForTesting",
            school_class=cls.school_class,
        )
        cls.subject = cls.create_subject()
        cls.create_lesson(cls.subject, cls.teacher, cls.school_class)

    def get_url(self, class_slug=None):
        class_slug = class_slug or self.school_class.slug

        return reverse(self.path_name, args=[class_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(class_slug="slug")

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def test_return_404_if_the_teacher_does_not_teach_the_class(self):
        school_class2 = self.create_class(number="2c")
        self.login(self.teacher)

        response = self.client.get(self.get_url(class_slug=school_class2.slug))

        self.assertEqual(response.status_code, 404)

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
        self.assertContains(response, self.student.student_detail_url)
