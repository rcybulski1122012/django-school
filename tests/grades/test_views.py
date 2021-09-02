from django.forms import HiddenInput
from django.test import TestCase
from django.urls import reverse

from django_school.apps.grades.models import (GRADE_ALREADY_EXISTS_MESSAGE,
                                              Grade)
from django_school.apps.grades.views import SUCCESS_GRADE_CREATE_MESSAGE
from tests.utils import (ClassesMixin, GradesMixin, LessonsMixin,
                         ResourceViewMixin, TeacherViewMixin, UsersMixin)


class GradeViewTestMixin(
    TeacherViewMixin,
    ResourceViewMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    GradesMixin,
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_user(
            username="student123", school_class=self.school_class
        )
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.grade_category = self.create_grade_category(
            self.subject, self.school_class
        )

    def get_url(self, class_slug=None, subject_slug=None):
        class_slug = class_slug or self.school_class.slug
        subject_slug = subject_slug or self.subject.slug

        return reverse(self.path_name, args=[class_slug, subject_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(subject_slug="does-not-exist", class_slug="4cm")

    def test_return_404_when_the_teacher_is_not_teaching_the_class(self):
        self.login(self.teacher)
        school_class2 = self.create_class(number="2c")

        response = self.client.get(self.get_url(class_slug=school_class2.slug))

        self.assertEqual(response.status_code, 404)

    def test_returns_404_when_the_class_does_not_learning_the_subject(self):
        self.login(self.teacher)
        self.lesson.delete()

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 404)

    def test_context_contains_class_slug_and_subject_slug(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertIn("class_slug", response.context)
        self.assertIn("subject_slug", response.context)


class TestGradeCreateView(GradeViewTestMixin, TestCase):
    path_name = "grades:add"

    def get_example_form_data(self):
        return {
            "grade": 5.00,
            "weight": 1,
            "comment": "Math Exam",
            "subject": self.subject.pk,
            "student": self.student.pk,
            "category": self.grade_category.pk,
            "teacher": self.teacher.pk,
        }

    def test_form_student_queryset(self):
        self.login(self.teacher)
        school_class2 = self.create_class(number="class2")
        self.create_user(username="student2", school_class=school_class2)

        response = self.client.get(self.get_url())

        students_qs = response.context["form"].fields["student"].queryset
        self.assertQuerysetEqual(students_qs, [self.student])

    def test_for_categories_queryset(self):
        self.login(self.teacher)
        school_class2 = self.create_class(number="class2")
        self.create_grade_category(self.subject, school_class2)

        response = self.client.get(self.get_url())

        categories_qs = response.context["form"].fields["category"].queryset
        self.assertQuerysetEqual(categories_qs, [self.grade_category])

    def test_creates_grade(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        self.client.post(self.get_url(), data)

        self.assertTrue(Grade.objects.exists())

    def test_redirect_after_successful_grade_adding(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data)

        self.assertRedirects(
            response,
            reverse(
                "grades:class_grades", args=[self.school_class.slug, self.subject.slug]
            ),
        )

    def test_teacher_and_subject_input_is_hidden(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())
        subject_field = response.context["form"].fields["subject"]
        teacher_field = response.context["form"].fields["teacher"]

        self.assertContains(
            response,
            f"<input type='hidden' name='teacher' value='{self.teacher.pk}' id='id_teacher'>",
            html=True,
        )
        self.assertContains(
            response,
            f"<input type='hidden' name='subject' value='{self.subject.pk}' id='id_subject'>",
            html=True,
        )
        self.assertIsInstance(subject_field.widget, HiddenInput)
        self.assertIsInstance(teacher_field.widget, HiddenInput)

    def test_displays_success_message_after_successful_create(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data, follow=True)

        self.assertContains(response, SUCCESS_GRADE_CREATE_MESSAGE)

    def test_set_student_initial_data_to_form_if_given(self):
        self.login(self.teacher)
        url = f"{self.get_url()}?student={self.student.pk}"

        response = self.client.get(url)

        form = response.context["form"]
        self.assertIn("student", form.initial),
        self.assertEqual(form.initial["student"], str(self.student.pk))

    def test_displays_error_after_adding_a_grade_which_already_exist(self):
        self.login(self.teacher)
        self.create_grade(self.grade_category, self.subject, self.student, self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data=data)

        self.assertContains(response, GRADE_ALREADY_EXISTS_MESSAGE, html=True)


class TestClassGradesView(GradeViewTestMixin, TestCase):
    path_name = "grades:class_grades"

    def test_context_contains_list_of_given_class_students(self):
        self.login(self.teacher)
        school_class2 = self.create_class(number="2c")
        self.create_user(username="student2", school_class=school_class2)

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(response.context["students"], [self.student])

    def test_context_contains_list_of_grade_categories_of_class_and_subject(self):
        self.login(self.teacher)
        subject2 = self.create_subject(name="sub2")
        school_class2 = self.create_class(number="2c")
        self.create_grade_category(self.subject, school_class2)
        self.create_grade_category(subject2, self.school_class)

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(response.context["categories"], [self.grade_category])
