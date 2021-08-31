from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from tests.utils import (ClassesMixin, CommonMixin, GradesMixin, LessonsMixin,
                         UsersMixin)

User = get_user_model()


class TestUserModel(
    UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, CommonMixin, TestCase
):
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

        teachers_group = Group.objects.get(name="teachers")
        user.groups.add(teachers_group)

        self.assertTrue(user.is_teacher)

    def test_with_nested_resources(self):
        address = self.create_address()
        user = self.create_user(address=address)

        with self.assertNumQueries(1):
            users = list(User.objects.with_nested_resources())

        with self.assertNumQueries(0):
            user = users[0]
            address = user.address

    def test_with_nested_student_resources(self):
        address = self.create_address()
        teacher = self.create_teacher()
        school_class = self.create_class(tutor=teacher)
        student = self.create_user(username="student", school_class=school_class)
        subject = self.create_subject()
        grade_category = self.create_grade_category(subject, school_class)
        grade = self.create_grade(grade_category, subject, student, teacher)

        with self.assertNumQueries(3):
            users = list(
                User.objects.with_nested_student_resources().filter(pk=student.pk)
            )

        with self.assertNumQueries(0):
            student_ = users[0]
            address_ = student_.address
            school_class_ = student_.school_class
            tutor_ = school_class_.tutor
            grade_ = student_.grades_gotten.all()[0]
            grade_category_ = grade_.category

    def test_with_nested_teacher_resources(self):
        address = self.create_address()
        teacher = self.create_teacher()
        school_class = self.create_class(tutor=teacher)
        student = self.create_user(username="student", school_class=school_class)
        subject = self.create_subject()
        grade_category = self.create_grade_category(subject, school_class)
        grade = self.create_grade(grade_category, subject, student, teacher)
        lesson = self.create_lesson(subject, teacher, school_class)

        with self.assertNumQueries(5):
            users = list(
                User.objects.with_nested_teacher_resources().filter(pk=teacher.pk)
            )

        with self.assertNumQueries(0):
            teacher_ = users[0]
            address_ = teacher_.address
            teacher_class = teacher_.teacher_class
            grade_ = teacher_.grades_added.all()[0]
            grade_category_ = grade_.category
            lessons = teacher_.lessons.all()
            lesson_subject = lessons[0].subject
