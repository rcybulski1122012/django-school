from django.test import TestCase

from django_school.apps.grades.forms import (BulkGradeCreationCommonInfoForm,
                                             BulkGradeCreationFormSet,
                                             GradeCategoryForm, GradeForm)
from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin


class GradeFormTestCase(UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_user(
            username="student", school_class=self.school_class
        )
        self.subject = self.create_subject()
        self.grade_category = self.create_grade_category(
            self.subject, self.school_class
        )

    def test_student_queryset(self):
        school_class2 = self.create_class(number="2c")
        self.create_user(username="student2", school_class=school_class2)

        form = GradeForm(
            school_class=self.school_class, subject=self.subject, teacher=self.teacher
        )

        student_qs = form.fields["student"].queryset
        self.assertQuerysetEqual(student_qs, [self.student])

    def test_category_queryset(self):
        subject2 = self.create_subject(name="subject2")
        school_class2 = self.create_class(number="2c")
        self.create_grade_category(self.subject, school_class2)
        self.create_grade_category(subject2, self.school_class)

        form = GradeForm(
            school_class=self.school_class, subject=self.subject, teacher=self.teacher
        )

        categories_qs = form.fields["category"].queryset
        self.assertQuerysetEqual(categories_qs, [self.grade_category])

    def test_is_valid_assigns_the_teacher_and_the_subject_to_the_instance(self):
        form = GradeForm(
            school_class=self.school_class, subject=self.subject, teacher=self.teacher
        )

        form.is_valid()

        self.assertEqual(form.instance.teacher, self.teacher)
        self.assertEqual(form.instance.subject, self.subject)


class BulkGradeCreationCommonInfoFormTestCase(
    UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_user(
            username="student", school_class=self.school_class
        )
        self.subject = self.create_subject()
        self.category = self.create_grade_category(self.subject, self.school_class)

    def test_category_queryset(self):
        subject2 = self.create_subject(name="subject2")
        school_class2 = self.create_class(number="2c")
        self.create_grade_category(subject2, self.school_class)
        self.create_grade_category(self.subject, school_class2)

        form = BulkGradeCreationCommonInfoForm(
            school_class=self.school_class, subject=self.subject
        )

        category_qs = form.fields["category"].queryset

        self.assertQuerysetEqual(category_qs, [self.category])


class BulkGradeCreationFormSetTestCase(UsersMixin, TestCase):
    def setUp(self):
        self.students = [self.create_user(username=f"username{i}") for i in range(5)]
        self.formset = BulkGradeCreationFormSet(students=self.students)

    def test_queryset_is_empty(self):
        self.assertQuerysetEqual(self.formset.queryset, [])

    def test_total_form_count_is_len_of_students(self):
        self.assertEqual(self.formset.total_form_count(), len(self.students))

    def test_sets_initial_value_of_student_field_to_every_form(self):
        students_initial_pks = {
            form.fields["student"].initial for form in self.formset.forms
        }
        students_pks = {student.pk for student in self.students}

        self.assertEqual(students_initial_pks, students_pks)

    def test_sets_common_data(self):
        common_data = {"test": 1, "common": 2, "data": 3}
        self.formset.set_common_data(common_data)

        data = self.formset.data
        self.assertEqual(data["form-0-test"], common_data["test"])
        self.assertEqual(data["form-0-common"], common_data["common"])
        self.assertEqual(data["form-0-data"], common_data["data"])

    def test_formset_html_does_not_contain_default_label(self):
        self.assertNotIn(
            '<label for="id_form-0-grade">Grade:</label>', self.formset.as_p()
        )


class GradeCategoryFormTestCase(ClassesMixin, LessonsMixin, TestCase):
    def setUp(self):
        self.subject = self.create_subject()
        self.school_class = self.create_class()

    def test_is_valid_assign_the_teacher_to_the_instance(self):
        form = GradeCategoryForm(subject=self.subject, school_class=self.school_class)

        form.is_valid()

        self.assertEqual(form.instance.subject, self.subject)
        self.assertEqual(form.instance.school_class, self.school_class)
