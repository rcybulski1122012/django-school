from django.core.exceptions import ValidationError
from django.test import TestCase

from django_school.apps.lessons.models import Presence, Subject
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

    def test_clean_raises_ValidationError_if_teacher_is_not_in_teachers_group(self):
        with self.assertRaises(ValidationError):
            self.create_lesson(self.subject, self.student, self.school_class).clean()


class PresenceModelTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
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
            Presence(student=student, lesson_session=lesson_session).clean()
