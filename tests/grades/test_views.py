from django.forms import HiddenInput
from django.test import TestCase
from django.urls import reverse

from django_school.apps.grades.models import (GRADE_ALREADY_EXISTS_MESSAGE,
                                              Grade)
from django_school.apps.grades.views import (
    SUCCESS_GRADE_CREATE_MESSAGE, SUCCESS_GRADE_DELETE_MESSAGE,
    SUCCESS_GRADE_UPDATE_MESSAGE, SUCCESS_IN_BULK_GRADES_CREATE_MESSAGE)
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

    def test_context_contains_school_class_and_subject(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertIn("school_class", response.context)
        self.assertIn("subject", response.context)


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

    def test_renders_avg_of_students_grades_with_precision_to_2_numbers(self):
        self.login(self.teacher)
        for grade in [1.5, 3.75, 5.5]:
            self.create_grade(
                self.grade_category, self.subject, self.student, self.teacher, grade
            )
        expected_avg = "3.58"

        response = self.client.get(self.get_url())

        self.assertContains(response, expected_avg)


class TestCreateGradesInBulkView(GradeViewTestMixin, TestCase):
    path_name = "grades:create_grades_in_bulk"

    def get_url(self, class_slug=None, subject_slug=None, category_pk=None):
        url = super().get_url(class_slug, subject_slug)

        if category_pk:
            url += f"?category={category_pk}"

        return url

    def prepare_form_data(self, students):
        students_count = len(students)
        data = {
            "weight": 1,
            "comment": "Math Exam",
            "subject": self.subject.pk,
            "category": self.grade_category.pk,
            "teacher": self.teacher.pk,
            "form-TOTAL_FORMS": students_count,
            "form-INITIAL_FORMS": 0,
        }

        for i, student in enumerate(students):
            data.update(
                {
                    f"form-{i}-student": student.pk,
                    f"form-{i}-grade": "3.0",
                    f"form-{i}-id": "",
                }
            )

        return data

    def test_set_category_initial_data_to_form_if_given(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url(category_pk=self.grade_category.pk))

        form = response.context["common_form"]
        self.assertEqual(form.initial["category"], str(self.grade_category.pk))

    def test_creates_grades(self):
        self.login(self.teacher)
        data = self.prepare_form_data([self.student])

        self.client.post(self.get_url(), data)

        self.assertTrue(Grade.objects.exists())

    def test_redirects_to_class_grades_after_successful_create(self):
        self.login(self.teacher)
        data = self.prepare_form_data([self.student])

        response = self.client.post(self.get_url(), data)

        self.assertRedirects(
            response,
            reverse(
                "grades:class_grades", args=[self.school_class.slug, self.subject.slug]
            ),
        )

    def test_displays_success_message_after_successful_create(self):
        self.login(self.teacher)
        data = self.prepare_form_data([self.student])

        response = self.client.post(self.get_url(), data, follow=True)

        self.assertContains(response, SUCCESS_IN_BULK_GRADES_CREATE_MESSAGE)

    def test_displays_error_when_students_already_have_grade_in_this_category(self):
        self.login(self.teacher)
        self.create_grade(self.grade_category, self.subject, self.student, self.teacher)
        data = self.prepare_form_data([self.student])

        response = self.client.post(self.get_url(), data)
        print(response.status_code)
        print(response.content)

        self.assertContains(response, GRADE_ALREADY_EXISTS_MESSAGE, html=True)


class TestGradeUpdateView(
    TeacherViewMixin,
    ResourceViewMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    GradesMixin,
    TestCase,
):
    path_name = "grades:update"

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
        self.grade = self.create_grade(
            self.grade_category, self.subject, self.student, self.teacher
        )

    def get_url(self, grade_pk=None):
        if grade_pk:
            return reverse(self.path_name, args=[grade_pk])
        else:
            return reverse(self.path_name, args=[self.grade.pk])

    def get_nonexistent_resource_url(self):
        return self.get_url(grade_pk=12345)

    @staticmethod
    def get_example_form_data():
        return {
            "grade": 5.0,
            "weight": 5,
            "comment": "Updated comment",
        }

    def test_updates_grade_when_data_is_correct(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        self.client.post(self.get_url(), data)

        self.grade.refresh_from_db()
        self.assertTrue(data.items() <= self.grade.__dict__.items())

    def test_redirects_to_class_grades_after_successful_update(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data)

        self.assertRedirects(
            response,
            reverse(
                "grades:class_grades", args=[self.school_class.slug, self.subject.slug]
            ),
        )

    def test_displays_success_message_after_successful_update(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data, follow=True)
        print(response.content)

        self.assertContains(response, SUCCESS_GRADE_UPDATE_MESSAGE)

    def test_renders_student_name_and_category_name(self):
        self.login(self.teacher)
        response = self.client.get(self.get_url())

        self.assertContains(response, self.student.full_name)
        self.assertContains(response, self.grade_category.name)

    def test_returns_403_when_user_is_not_the_teacher_who_gave_the_grade(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 403)


class TestGradeDeleteView(
    TeacherViewMixin,
    ResourceViewMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    GradesMixin,
    TestCase,
):
    path_name = "grades:delete"

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
        self.grade = self.create_grade(
            self.grade_category, self.subject, self.student, self.teacher
        )

    def get_url(self, grade_pk=None):
        if grade_pk:
            return reverse(self.path_name, args=[grade_pk])
        else:
            return reverse(self.path_name, args=[self.grade.pk])

    def get_nonexistent_resource_url(self):
        return self.get_url(grade_pk=12345)

    def test_deletes(self):
        self.login(self.teacher)

        self.client.post(self.get_url())

        self.assertFalse(Grade.objects.exists())

    def test_redirects_to_class_grades_after_successful_delete(self):
        self.login(self.teacher)

        response = self.client.post(self.get_url())

        self.assertRedirects(
            response,
            reverse(
                "grades:class_grades", args=[self.school_class.slug, self.subject.slug]
            ),
        )

    def test_displays_success_message_after_successful_delete(self):
        self.login(self.teacher)

        response = self.client.post(self.get_url(), follow=True)

        self.assertContains(response, SUCCESS_GRADE_DELETE_MESSAGE)

    def test_renders_grade_info(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.grade.get_grade_display())
        self.assertContains(response, self.grade_category.name)
        self.assertContains(response, self.student.full_name)

    def test_returns_403_when_user_is_not_the_teacher_who_gave_the_grade(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 403)
