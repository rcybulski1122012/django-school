from django.template import loader
from django.test import TestCase
from django.urls import reverse

from tests.utils import (ClassesMixin, GradesMixin, LessonsMixin,
                         ResourceViewTestMixin, RolesRequiredTestMixin,
                         UsersMixin)


class ClassListViewTestCase(
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

    def test_selects_classes_taught_by_teacher(self):
        school_class2 = self.create_class(number="2c")
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertNotIn(school_class2, response.context["school_classes"])

    def test_context_contains_list_of_classes_ordered_by_number(self):
        self.login(self.teacher)
        school_class2 = self.create_class(number="3c")
        school_class3 = self.create_class(number="2b")
        self.create_lesson(self.subject, self.teacher, school_class2)
        self.create_lesson(self.subject, self.teacher, school_class3)

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(
            response.context["school_classes"],
            [self.school_class, school_class3, school_class2],
        )

    def test_renders_appropriate_message_if_there_are_no_classes(self):
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

    def test_return_404_if_teacher_does_not_teach_class(self):
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


class ClassSummaryPDFViewTestCase(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    GradesMixin,
    TestCase,
):
    path_name = "classes:summary_pdf"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class(tutor=cls.teacher)
        cls.student1 = cls.create_student(
            school_class=cls.school_class, first_name="AStudentName"
        )
        cls.student2 = cls.create_student(
            school_class=cls.school_class,
            first_name="ZStudentName",
            username="student2",
        )
        cls.subject = cls.create_subject()
        cls.grade_category = cls.create_grade_category(cls.subject, cls.school_class)
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.lesson_session = cls.create_lesson_session(cls.lesson)
        cls.grade1 = cls.create_grade(
            cls.grade_category, cls.subject, cls.student1, cls.teacher
        )
        cls.grade2 = cls.create_grade(
            cls.grade_category,
            cls.subject,
            cls.student1,
            cls.teacher,
            grade=4.50,
        )
        cls.grade3 = cls.create_grade(
            cls.grade_category,
            cls.subject,
            cls.student2,
            cls.teacher,
            grade=1.50,
        )

        for status in ["present", "present", "absent"]:
            cls.create_attendance(
                cls.lesson_session, [cls.student1, cls.student2], status=status
            )

    def get_url(self, class_slug=None):
        class_slug = class_slug or self.school_class.slug

        return reverse(self.path_name, args=[class_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(class_slug="does-not-exist")

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student1

    @staticmethod
    def _get_html_content(response):
        context = {}
        for dict_ in response.context:
            context.update(dict_)

        return loader.get_template(response.template_name[0]).render(context)

    def test_returns_404_if_teacher_is_not_tutor_of_class(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 404)

    def test_renders_students_full_names(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())
        content = self._get_html_content(response)

        self.assertIn(self.student1.full_name, content)
        self.assertIn(self.student2.full_name, content)

    def test_renders_subjects_and_grades(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())
        content = self._get_html_content(response)

        self.assertIn(self.subject.name, content)
        expected_grades_str = (
            f"{self.grade1.get_grade_display()}, {self.grade2.get_grade_display()}"
        )
        self.assertIn(expected_grades_str, content)
        self.assertIn("1+", content)

    def test_renders_attendance(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())
        content = self._get_html_content(response)

        self.assertIn("67%", content)
        self.assertIn("<td>2</td>", content)
        self.assertIn("33%", content)
        self.assertIn("<td>1</td>", content)
        self.assertIn("<td>3</td>", content)

    def test_does_not_renders_empty_page_at_the_end(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        pages_count = len(response.get_document().pages)
        self.assertEqual(pages_count, 2)
        self.assertEqual(response.context["last_student"], self.student2)
