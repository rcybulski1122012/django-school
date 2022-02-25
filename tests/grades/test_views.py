from django.test import TestCase
from django.urls import reverse

from django_school.apps.grades.forms import GradeCategoryForm
from django_school.apps.grades.models import Grade, GradeCategory
from tests.utils import (AjaxRequiredTestMixin, ClassesMixin, GradesMixin,
                         LessonsMixin, LoginRequiredTestMixin,
                         ResourceViewTestMixin, RolesRequiredTestMixin,
                         UsersMixin)


class SubjectAndSchoolClassRelatedTestMixin(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    GradesMixin,
):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.category = cls.create_grade_category(cls.subject, cls.school_class)

    def get_url(self, class_slug=None, subject_slug=None):
        class_slug = class_slug or self.school_class.slug
        subject_slug = subject_slug or self.subject.slug

        return reverse(self.path_name, args=[class_slug, subject_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(subject_slug="does-not-exist", class_slug="4cm")

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def test_returns_404_if_teacher_is_not_teaching_class(self):
        self.login(self.teacher)
        school_class2 = self.create_class(number="2c")

        response = self.client.get(self.get_url(class_slug=school_class2.slug))

        self.assertEqual(response.status_code, 404)

    def test_returns_404_if_class_does_not_learning_subject(self):
        self.login(self.teacher)
        self.lesson.delete()

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 404)

    def test_context_contains_school_class_and_subject(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertEqual(response.context["school_class"], self.school_class)
        self.assertEqual(response.context["subject"], self.subject)


class GradeCreateViewTestCase(SubjectAndSchoolClassRelatedTestMixin, TestCase):
    path_name = "grades:add"

    def get_example_form_data(self):
        return {
            "grade": 5.00,
            "weight": 1,
            "comment": "Math Exam",
            "student": self.student.pk,
            "category": self.category.pk,
        }

    def test_creates_grade(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        self.client.post(self.get_url(), data)

        self.assertTrue(Grade.objects.exists())

    def test_redirect_to_class_grades_after_successful_create(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data)

        self.assertRedirects(
            response,
            reverse(
                "grades:class_grades", args=[self.school_class.slug, self.subject.slug]
            ),
        )

    def test_renders_success_message_after_successful_create(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data, follow=True)

        self.assertContains(response, "The grade has been added successfully.")

    def test_renders_error_after_adding_grade_which_already_exist(self):
        self.login(self.teacher)
        self.create_grade(self.category, self.subject, self.student, self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data=data)

        self.assertContains(
            response, "The student already has got a grade in this category.", html=True
        )

    def test_sets_student_initial_data_to_form_if_given(self):
        self.login(self.teacher)
        url = f"{self.get_url()}?student={self.student.pk}"

        response = self.client.get(url)

        form = response.context["form"]
        self.assertEqual(form.initial["student"], str(self.student.pk))


class ClassGradesViewTestCase(SubjectAndSchoolClassRelatedTestMixin, TestCase):
    path_name = "grades:class_grades"

    def test_context_contains_list_of_given_class_students(self):
        self.login(self.teacher)
        school_class2 = self.create_class(number="2c")
        self.create_student(username="student2", school_class=school_class2)

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(response.context["students"], [self.student])

    def test_context_contains_list_of_grade_categories_of_class_and_subject(self):
        self.login(self.teacher)
        subject2 = self.create_subject(name="sub2")
        school_class2 = self.create_class(number="2c")
        self.create_grade_category(self.subject, school_class2)
        self.create_grade_category(subject2, self.school_class)

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(response.context["categories"], [self.category])

    def test_renders_avg_of_students_grades_with_precision_to_2_numbers(self):
        self.login(self.teacher)
        for grade in [1.5, 3.75, 5.5]:
            self.create_grade(
                self.category, self.subject, self.student, self.teacher, grade
            )
        expected_avg = "3.58"

        response = self.client.get(self.get_url())

        self.assertContains(response, expected_avg)


class StudentGradesViewTestCase(
    LoginRequiredTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    GradesMixin,
    TestCase,
):
    path_name = "grades:student_grades"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.category = cls.create_grade_category(cls.subject, cls.school_class)
        cls.grade = cls.create_grade(
            cls.category, cls.subject, cls.student, cls.teacher
        )

    def get_url(self, student_slug=None):
        student_slug = student_slug or self.student.slug

        return reverse(self.path_name, args=[student_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(student_slug="does-not-exist")

    def get_permitted_user(self):
        return self.student

    def test_returns_404_if_user_with_given_slug_is_not_student(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url(student_slug=self.teacher.slug))

        self.assertEqual(response.status_code, 404)

    def test_returns_404_if_student_is_not_visible_to_user(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 404)

    def test_context_contains_list_of_subjects_and_dict_of_averages(self):
        self.login(self.teacher)
        for grade, weight in [("2", 3), ("2", 2), ("4", 1), ("5", 1), ("4", 2)]:
            self.create_grade(
                self.category, self.subject, self.student, self.teacher, grade, weight
            )

        response = self.client.get(self.get_url())

        subjects = response.context["subjects"]
        averages = response.context["averages"]
        self.assertEqual(subjects, [self.subject])
        self.assertEqual(averages, {self.DEFAULT_SUBJECT_NAME: 3.00})

    def test_sets_grades_seen_by_student_attr_to_True_if_user_is_student(self):
        self.assertFalse(self.grade.seen_by_student)
        self.login(self.student)

        self.client.get(self.get_url())
        self.grade.refresh_from_db()

        self.assertTrue(self.grade.seen_by_student)

    def test_sets_grades_seen_by_parent_attr_to_True_if_user_is_parent(self):
        parent = self.create_parent(child=self.student)
        self.assertFalse(self.grade.seen_by_parent)
        self.login(parent)

        self.client.get(self.get_url())
        self.grade.refresh_from_db()

        self.assertTrue(self.grade.seen_by_parent)


class GradeBulkCreateViewTestCase(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    GradesMixin,
    TestCase,
):
    path_name = "grades:add_in_bulk"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.category = cls.create_grade_category(cls.subject, cls.school_class)

    def get_url(self, category_pk=None):
        category_pk = category_pk or self.category.pk

        return reverse(self.path_name, args=[category_pk])

    def get_nonexistent_resource_url(self):
        return self.get_url(category_pk=12345)

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    @staticmethod
    def get_example_form_data(students):
        students_count = len(students)
        data = {
            "weight": 1,
            "comment": "Math Exam",
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

    def test_returns_404_if_class_does_not_learning_subject(self):
        self.login(self.teacher)
        self.lesson.delete()

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 404)

    def test_returns_404_if_every_student_already_has_grade_in_category(self):
        self.login(self.teacher)
        self.create_grade(self.category, self.subject, self.student, self.teacher)

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 404)

    def test_context_contains_school_class_subject_and_category(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertEqual(response.context["school_class"], self.school_class)
        self.assertEqual(response.context["subject"], self.subject)
        self.assertEqual(response.context["category"], self.category)

    def test_creates_grades(self):
        self.login(self.teacher)
        data = self.get_example_form_data([self.student])

        self.client.post(self.get_url(), data)

        self.assertTrue(Grade.objects.exists())

    def test_redirects_to_class_grades_after_successful_create(self):
        self.login(self.teacher)
        data = self.get_example_form_data([self.student])

        response = self.client.post(self.get_url(), data)

        self.assertRedirects(
            response,
            reverse(
                "grades:class_grades", args=[self.school_class.slug, self.subject.slug]
            ),
        )

    def test_renders_success_message_after_successful_create(self):
        self.login(self.teacher)
        data = self.get_example_form_data([self.student])

        response = self.client.post(self.get_url(), data, follow=True)

        self.assertContains(response, "The grades have been added successfully.")

    def test_excludes_students_if_they_already_have_grade_in_category(self):
        self.login(self.teacher)
        student2 = self.create_student(
            username="student2",
            school_class=self.school_class,
            first_name="Student2",
            last_name="BulkCreationTestCase",
        )
        self.create_grade(self.category, self.subject, student2, self.teacher)

        response = self.client.get(self.get_url())

        self.assertNotContains(response, student2.full_name)
        self.assertContains(response, self.student.full_name)


class SingleGradeTestMixin(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    GradesMixin,
):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.category = cls.create_grade_category(cls.subject, cls.school_class)
        cls.grade = cls.create_grade(
            cls.category, cls.subject, cls.student, cls.teacher
        )

    def get_url(self, grade_pk=None):
        grade_pk = grade_pk or self.grade.pk

        return reverse(self.path_name, args=[grade_pk])

    def get_nonexistent_resource_url(self):
        return self.get_url(grade_pk=12345)

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def test_returns_404_if_user_is_not_teacher_who_gave_grade(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        if self.ajax_required:
            response = self.client.post(self.get_url())
        else:
            response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 404)


class GradeUpdateViewTestCase(SingleGradeTestMixin, TestCase):
    path_name = "grades:update"

    @staticmethod
    def get_example_form_data():
        return {
            "grade": 5.0,
            "weight": 5,
            "comment": "Updated comment",
        }

    def test_updates_grade(self):
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

    def test_renders_success_message_after_successful_update(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data, follow=True)

        self.assertContains(response, "The grade has been updated successfully.")

    def test_renders_student_name_and_category_name(self):
        self.login(self.teacher)
        response = self.client.get(self.get_url())

        self.assertContains(response, self.student.full_name)
        self.assertContains(response, self.category.name)


class GradeDeleteViewTestCase(SingleGradeTestMixin, AjaxRequiredTestMixin, TestCase):
    path_name = "grades:delete"
    ajax_required = True

    def test_deletes_grade(self):
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

    def test_renders_success_message_after_successful_delete(self):
        self.login(self.teacher)

        response = self.client.post(self.get_url(), follow=True)

        self.assertContains(response, "The grade has been deleted successfully.")


class GradeCategoryFormViewTestCase(ClassesMixin, LessonsMixin, GradesMixin, TestCase):
    def test_context_contains_GradeCategoryForm(self):
        response = self.client.get(reverse("grades:categories:form"))

        form = response.context["form"]
        self.assertIsInstance(form, GradeCategoryForm)


class GradeCategoriesViewTestCase(SubjectAndSchoolClassRelatedTestMixin, TestCase):
    path_name = "grades:categories:create"

    def test_returns_404_if_teacher_is_not_teaching_subject_to_class(
        self,
    ):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 404)

    def test_renders_list_of_categories_if_request_method_is_GET(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        categories = response.context["categories"]
        self.assertQuerysetEqual(categories, [self.category])
        self.assertContains(response, self.category.name)

    def test_context_contains_school_class_and_subject_if_request_method_is_GET(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertEqual(response.context["subject"], self.subject)
        self.assertEqual(response.context["school_class"], self.school_class)

    def test_creates_category_and_redirects_to_category_detail_if_data_is_valid_and_request_method_is_POST(  # noqa
        self,
    ):
        self.login(self.teacher)

        response = self.client.post(self.get_url(), {"name": "new category"})

        new_category = GradeCategory.objects.exclude(pk=self.category.pk).get()

        self.assertRedirects(response, new_category.detail_url)

    def test_renders_grade_category_form_if_data_is_invalid_and_request_method_is_POST(
        self,
    ):
        self.login(self.teacher)

        response = self.client.post(self.get_url(), {"name": "a" * 65})

        self.assertTemplateUsed(response, "grades/partials/grade_category_form.html")
        self.assertIn("form", response.context)


class SingleGradeCategoryTestMixin(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    GradesMixin,
):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.category = cls.create_grade_category(cls.subject, cls.school_class)

    def get_url(self, pk=None, **kwargs):
        pk = pk or self.category.pk

        return reverse(self.path_name, args=[pk])

    def get_nonexistent_resource_url(self):
        return self.get_url(pk=12345)

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def test_returns_404_if_teacher_is_not_teaching_subject_to_class(
        self,
    ):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        params = (
            {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"} if self.ajax_required else {}
        )
        response = self.client.get(self.get_url(), **params)

        self.assertEqual(response.status_code, 404)


class GradeCategoryDetailViewTestCase(SingleGradeCategoryTestMixin, TestCase):
    path_name = "grades:categories:detail"

    def test_renders_name_of_category(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertEqual(response.context["category"], self.category)
        self.assertContains(response, self.category.name)


class GradeCategoryDeleteViewTestCase(
    SingleGradeCategoryTestMixin, AjaxRequiredTestMixin, TestCase
):
    path_name = "grades:categories:delete"
    ajax_required = True

    def test_deletes_category(self):
        self.login(self.teacher)

        self.ajax_request(self.get_url(), method="post")

        self.assertFalse(GradeCategory.objects.exists())

    def test_redirects_to_categories_list_after_successful_delete(self):
        self.login(self.teacher)

        response = self.ajax_request(self.get_url(), method="post")

        expected_url = reverse(
            "grades:categories:create", args=[self.school_class.slug, self.subject.slug]
        )
        self.assertRedirects(response, expected_url)


class GradeCategoryUpdateViewTestCase(SingleGradeCategoryTestMixin, TestCase):
    path_name = "grades:categories:update"

    def get_example_form_data(self):
        return {
            "name": "new name",
            "subject": self.subject.pk,
            "school_class": self.school_class.pk,
        }

    def test_updates_category(self):
        self.login(self.teacher)

        self.client.post(self.get_url(), self.get_example_form_data())

        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "new name")

    def test_redirects_to_category_detail_after_successful_update(self):
        self.login(self.teacher)

        response = self.client.post(self.get_url(), self.get_example_form_data())

        self.assertRedirects(response, self.category.detail_url)
