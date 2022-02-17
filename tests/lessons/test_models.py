from django.core.exceptions import ValidationError
from django.test import TestCase

from django_school.apps.lessons.models import (Attendance, LessonSession,
                                               Subject)
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class SubjectModelTestCase(LessonsMixin, TestCase):
    def test_save_slugify_if_slug_not_given(self):
        subject = self.create_subject(name="Computer Science")

        self.assertEqual(subject.slug, "computer-science")

    def test_save_does_not_slugify_if_slug_given(self):
        subject = self.create_subject(name="Computer Science", slug="cs")

        self.assertEqual(subject.slug, "cs")


class SubjectQuerySetTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.subject = self.create_subject()

    def test_with_does_the_teacher_teach_the_subject_to_the_class_when_does_not_teach(
        self,
    ):
        subject = Subject.objects.with_does_the_teacher_teach_the_subject_to_the_class(
            self.teacher, self.school_class
        ).get()

        self.assertFalse(subject.does_the_teacher_teach_the_subject_to_the_class)

    def test_with_does_the_teacher_teach_the_subject_to_the_class_when_teaches(self):
        self.create_lesson(self.subject, self.teacher, self.school_class)
        subject = Subject.objects.with_does_the_teacher_teach_the_subject_to_the_class(
            self.teacher, self.school_class
        ).get()

        self.assertTrue(subject.does_the_teacher_teach_the_subject_to_the_class)


class LessonModelTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(school_class=self.school_class)
        self.subject = self.create_subject()

    def test_clean_raises_ValidationError_when_the_teacher_already_have_lesson_in_given_time(
        self,
    ):
        self.create_lesson(self.subject, self.teacher, self.school_class)

        with self.assertRaises(ValidationError):
            self.create_lesson(self.subject, self.teacher, self.school_class).clean()

    def test_clean_raises_ValidationError_if_teacher_is_not_a_teacher(self):
        with self.assertRaises(ValidationError):
            self.create_lesson(self.subject, self.student, self.school_class).clean()


class LessonSessionQuerySetTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(school_class=self.school_class)
        self.parent = self.create_parent()
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.lesson_session = self.create_lesson_session(self.lesson)

    def test_visible_to_user_returns_none_if_user_is_a_parent(self):
        qs = LessonSession.objects.visible_to_user(self.parent)

        self.assertQuerysetEqual(qs, LessonSession.objects.none())

    def test_visible_to_user_returns_teacher_lessons_if_user_is_a_teacher(self):
        teacher2 = self.create_teacher(username="teacher2")
        lesson2 = self.create_lesson(self.subject, teacher2, self.school_class)
        self.create_lesson_session(lesson2)

        qs = LessonSession.objects.visible_to_user(self.teacher)

        self.assertQuerysetEqual(qs, [self.lesson_session])

    def test_visible_to_user_returns_class_lessons_if_user_is_a_student(self):
        school_class2 = self.create_class(number="2c")
        lesson2 = self.create_lesson(self.subject, self.teacher, school_class2)
        self.create_lesson_session(lesson2)

        qs = LessonSession.objects.visible_to_user(self.student)

        self.assertQuerysetEqual(qs, [self.lesson_session])


class AttendanceModelTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    def test_clean_raises_ValidationError_if_student_is_not_in_lesson_session_class(
        self,
    ):
        teacher = self.create_teacher()
        school_class = self.create_class()
        student = self.create_student()
        subject = self.create_subject()
        lesson = self.create_lesson(subject, teacher, school_class)
        lesson_session = self.create_lesson_session(lesson)

        with self.assertRaises(ValidationError):
            Attendance(student=student, lesson_session=lesson_session).clean()
