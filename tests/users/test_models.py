from django.contrib.auth import get_user_model
from django.test import TestCase

from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin

User = get_user_model()


class TestUserModel(UsersMixin, TestCase):
    def test_full_name(self):
        user = self.create_user(first_name="FirstName", last_name="LastName")

        self.assertEqual(user.full_name, "FirstName LastName")

    def test_slugify_on_save_if_slug_not_given(self):
        user = User.objects.create(first_name="FirstName", last_name="LastName")

        self.assertEqual(user.slug, "firstname-lastname")

    def test_does_not_slugify_if_slug_given(self):
        user = self.create_user(slug="slug")

        self.assertEqual(user.slug, "slug")

    def test_is_teacher(self):
        user = self.create_user()

        self.assertFalse(user.is_teacher)

        self.add_user_to_group(user, "teachers")

        self.assertTrue(user.is_teacher)


class TestCustomUserManager(
    UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase
):
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

    def test_with_weighted_avg_of_given_subject(self):
        subject2 = self.create_subject(name="subject2")
        grades_of_subject = [
            self.create_grade(
                self.grade_category, self.subject, self.student, self.teacher, grade
            )
            for grade in [1, 1.5, 5.5, 6.75]
        ]

        grades_of_subject2 = [
            self.create_grade(
                self.grade_category, subject2, self.student, self.teacher, grade
            )
            for grade in [1.75, 3.5, 6, 1]
        ]

        w_avg_in_subject1 = (
            User.objects.with_weighted_avg(self.subject).get(pk=self.student.pk).w_avg
        )
        w_avg_in_subject2 = (
            User.objects.with_weighted_avg(subject2).get(pk=self.student.pk).w_avg
        )

        self.assertAlmostEqual(w_avg_in_subject1, 3.6875)
        self.assertAlmostEqual(w_avg_in_subject2, 3.0625)

    def test_with_weighted_avg_cares_about_weights(self):
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
            User.objects.with_weighted_avg(self.subject).get(pk=self.student.pk).w_avg
        )

        self.assertAlmostEqual(w_avg, 3.833333333333333)

    def test_with_weighted_avg_when_no_grades(self):
        user = User.objects.with_weighted_avg(self.subject).get(pk=self.student.pk)
        self.assertIsNone(user.w_avg)

    def test_with_weighted_avg_does_not_filter_users_qs(self):
        student2 = self.create_user(username="student2")
        self.create_grade(self.grade_category, self.subject, self.student, self.teacher)
        # TODO: User.students.with_weighted_avg(self.subject)
        users = User.objects.with_weighted_avg(self.subject).exclude(
            groups__name="teachers"
        )

        self.assertQuerysetEqual(users, [self.student, student2], ordered=False)
