import datetime
from unittest import skip

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from django_school.apps.lessons.models import Attendance
from django_school.apps.users.models import ROLES
from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin

User = get_user_model()


class UserModelTestCase(UsersMixin, ClassesMixin, TestCase):
    def test_full_name(self):
        user = self.create_user(first_name="FirstName", last_name="LastName")

        self.assertEqual(user.full_name, "FirstName LastName")

    def test_save_slugify_if_slug_not_given(self):
        user = User.objects.create(first_name="FirstName", last_name="LastName")

        self.assertEqual(user.slug, "firstname-lastname")

    def test_save_does_not_slugify_if_slug_given(self):
        user = self.create_user(slug="slug")

        self.assertEqual(user.slug, "slug")

    def test_is_teacher(self):
        user = self.create_user()

        self.assertFalse(user.is_teacher)

        user.role = ROLES.TEACHER
        user.save()

        self.assertTrue(user.is_teacher)

    def test_is_student(self):
        user = self.create_user()

        self.assertFalse(user.is_student)

        user.role = ROLES.STUDENT
        user.save()

        self.assertTrue(user.is_student)

    def test_is_parent(self):
        user = self.create_user()

        self.assertFalse(user.is_parent)

        user.role = ROLES.PARENT
        user.save()

        self.assertTrue(user.is_parent)

    def test_clean_raises_ValidationError_if_user_is_not_a_student_and_has_class_assigned(
        self,
    ):
        school_class = self.create_class()
        user = User()
        user.clean()

        user.role = ROLES.TEACHER
        user.school_class = school_class

        with self.assertRaises(ValidationError):
            user.clean()

    def test_clean_raises_ValidationError_if_user_is_not_a_parent_and_has_child_assigned(
        self,
    ):
        student = self.create_student()
        user = User()
        user.clean()

        user.role = ROLES.TEACHER
        user.child = student

        with self.assertRaises(ValidationError):
            user.clean()

    def test_clean_raises_ValidationError_if_child_is_not_a_student(self):
        parent = self.create_parent()
        teacher = self.create_teacher()
        parent.clean()

        parent.child = teacher

        with self.assertRaises(ValidationError):
            parent.clean()


class StudentsManagerTestCase(
    UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(school_class=self.school_class)
        self.subject = self.create_subject()
        self.grade_category = self.create_grade_category(
            self.subject, self.school_class
        )

    def test_selects_only_students(self):
        students = User.students.all()

        self.assertQuerysetEqual(students, [self.student])

    def test_with_weighted_avg_for_subject_of_given_subject(self):
        subject2 = self.create_subject(name="subject2")
        [
            self.create_grade(
                self.grade_category, self.subject, self.student, self.teacher, grade
            )
            for grade in [1, 1.5, 5.5, 6.75]
        ]

        [
            self.create_grade(
                self.grade_category, subject2, self.student, self.teacher, grade
            )
            for grade in [1.75, 3.5, 6, 1]
        ]

        w_avg_in_subject1 = (
            User.students.with_weighted_avg_for_subject(self.subject)
            .get(pk=self.student.pk)
            .w_avg
        )
        w_avg_in_subject2 = (
            User.students.with_weighted_avg_for_subject(subject2)
            .get(pk=self.student.pk)
            .w_avg
        )

        self.assertAlmostEqual(w_avg_in_subject1, 3.6875)
        self.assertAlmostEqual(w_avg_in_subject2, 3.0625)

    def test_with_weighted_avg_for_subject_cares_about_weights(self):
        for grade, weight in [(3, 3), (4.5, 2), (5, 1)]:
            self.create_grade(
                self.grade_category,
                self.subject,
                self.student,
                self.teacher,
                grade,
                weight,
            )

        w_avg = (
            User.students.with_weighted_avg_for_subject(self.subject)
            .get(pk=self.student.pk)
            .w_avg
        )

        self.assertAlmostEqual(w_avg, 3.833333333333333)

    def test_with_weighted_avg_for_subject_when_no_grades(self):
        user = User.students.with_weighted_avg_for_subject(self.subject).get(
            pk=self.student.pk
        )
        self.assertIsNone(user.w_avg)

    def test_with_weighted_avg_for_subject_does_not_filter_users_qs(self):
        student2 = self.create_student(username="student2")
        self.create_grade(self.grade_category, self.subject, self.student, self.teacher)
        users = User.students.with_weighted_avg_for_subject(self.subject)

        self.assertQuerysetEqual(users, [self.student, student2], ordered=False)

    @skip("Works fine on linux, but not on windows")
    def test_with_subject_grades_selects_grades_of_given_subject(self):
        subject2 = self.create_subject(name="subject2")
        grades_of_subject = [
            self.create_grade(
                self.grade_category, self.subject, self.student, self.teacher
            )
            for _ in range(5)
        ]
        [
            self.create_grade(self.grade_category, subject2, self.student, self.teacher)
            for _ in range(5)
        ]

        grades = User.students.with_subject_grades(self.subject).get().subject_grades

        self.assertQuerysetEqual(grades, grades_of_subject)

    def test_with_subject_grades_performs_optimal_number_of_queries(self):
        for _ in range(5):
            self.create_grade(
                self.grade_category, self.subject, self.student, self.teacher
            )

        with self.assertNumQueries(2):
            _ = User.students.with_subject_grades(self.subject).get().subject_grades

    def test_visible_to_user_selects_taught_students_if_the_user_is_a_teacher(self):
        school_class2 = self.create_class(number="2c")
        self.create_student(username="student2", school_class=school_class2)
        teacher2 = self.create_teacher(username="teacher2")
        self.create_lesson(self.subject, teacher2, school_class2)
        self.create_lesson(self.subject, self.teacher, self.school_class)

        queryset = User.students.visible_to_user(self.teacher)
        self.assertQuerysetEqual(queryset, [self.student])

    def test_visible_to_user_selects_the_user_if_the_user_is_a_student(self):
        self.create_student(username="student2")
        queryset = User.students.visible_to_user(self.student)

        self.assertQuerysetEqual(queryset, [self.student])

    def test_visible_to_user_selects_the_child_if_the_user_is_a_parent(self):
        parent = self.create_parent(child=self.student)
        queryset = User.students.visible_to_user(parent)

        self.assertQuerysetEqual(queryset, [self.student])

    def test_with_attendance(self):
        lesson = self.create_lesson(self.subject, self.teacher, self.school_class)
        lesson_session = self.create_lesson_session(lesson, datetime.datetime.today())
        for status in Attendance.ATTENDANCE_STATUSES:
            self.create_attendance(lesson_session, [self.student], status=status[0])

        student = User.students.with_attendance().get()

        self.assertEqual(student.total_attendance, 4)
        self.assertEqual(student.present_hours, 1)
        self.assertEqual(student.absent_hours, 1)
        self.assertEqual(student.exempt_hours, 1)
        self.assertEqual(student.excused_hours, 1)

    def test_with_homework_realisations_selects_realisations_of_given_homework(self):
        student2 = self.create_student(
            username="student2", school_class=self.school_class
        )
        homework1 = self.create_homework(self.subject, self.teacher, self.school_class)
        homework2 = self.create_homework(self.subject, self.teacher, self.school_class)
        homework1_realisation = self.create_realisation(homework1, self.student)
        self.create_realisation(homework2, self.student)
        self.create_realisation(homework1, student2)

        student = User.students.with_homework_realisations(homework1).get(
            pk=self.student.pk
        )

        self.assertEqual(student.realisation, [homework1_realisation])

    def test_exclude_if_has_grade_in_category(self):
        student2 = self.create_student(
            username="student2", school_class=self.school_class
        )
        self.create_grade(self.grade_category, self.subject, student2, self.teacher)

        qs = User.students.exclude_if_has_grade_in_category(self.grade_category)

        self.assertQuerysetEqual(qs, [self.student])


class TeachersManagerTestCase(UsersMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.student = self.create_student()

    def test_selects_only_teachers(self):
        teachers = User.teachers.all()

        self.assertQuerysetEqual(teachers, [self.teacher])
