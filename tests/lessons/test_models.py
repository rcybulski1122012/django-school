import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from django_school.apps.lessons.models import (Attendance, Homework,
                                               LessonSession, Subject)
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class SubjectModelTestCase(LessonsMixin, TestCase):
    def test_save_slugifies_if_slug_not_given(self):
        subject = self.create_subject(name="Computer Science")

        self.assertEqual(subject.slug, "computer-science")

    def test_save_does_not_slugify_if_slug_given(self):
        subject = self.create_subject(name="Computer Science", slug="cs")

        self.assertEqual(subject.slug, "cs")


class SubjectQuerySetTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.subject = cls.create_subject()

    def test_with_does_the_teacher_teach_the_subject_to_the_class_if_user_does_not_teach(
        self,
    ):
        subject = Subject.objects.with_does_the_teacher_teach_the_subject_to_the_class(
            self.teacher, self.school_class
        ).get()

        self.assertFalse(subject.does_the_teacher_teach_the_subject_to_the_class)

    def test_with_does_the_teacher_teach_the_subject_to_the_class_if_user_teaches(self):
        self.create_lesson(self.subject, self.teacher, self.school_class)
        subject = Subject.objects.with_does_the_teacher_teach_the_subject_to_the_class(
            self.teacher, self.school_class
        ).get()

        self.assertTrue(subject.does_the_teacher_teach_the_subject_to_the_class)


class LessonModelTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()

    def test_clean_raises_ValidationError_if_teacher_already_have_lesson_in_given_time(
        self,
    ):
        self.create_lesson(self.subject, self.teacher, self.school_class)

        with self.assertRaises(ValidationError):
            self.create_lesson(self.subject, self.teacher, self.school_class).clean()

    def test_clean_raises_ValidationError_if_teacher_is_not_teacher(self):
        with self.assertRaises(ValidationError):
            self.create_lesson(self.subject, self.student, self.school_class).clean()


class LessonSessionQuerySetTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.parent = cls.create_parent()
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.lesson_session = cls.create_lesson_session(cls.lesson)

    def test_visible_to_user_returns_none_if_user_is_parent(self):
        qs = LessonSession.objects.visible_to_user(self.parent)

        self.assertQuerysetEqual(qs, LessonSession.objects.none())

    def test_visible_to_user_returns_teacher_lessons_if_user_is_teacher(self):
        teacher2 = self.create_teacher(username="teacher2")
        lesson2 = self.create_lesson(self.subject, teacher2, self.school_class)
        self.create_lesson_session(lesson2)

        qs = LessonSession.objects.visible_to_user(self.teacher)

        self.assertQuerysetEqual(qs, [self.lesson_session])

    def test_visible_to_user_returns_class_lessons_if_user_is_student(self):
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


class HomeworkQuerySetTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.homework = cls.create_homework(cls.subject, cls.teacher, cls.school_class)

    def test_visible_to_user_returns_homeworks_set_if_user_is_teacher(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.create_homework(self.subject, teacher2, self.school_class)

        qs = Homework.objects.visible_to_user(self.teacher)

        self.assertQuerysetEqual(qs, [self.homework])

    def test_visible_to_user_returns_class_homeworks_if_user_is_student(self):
        school_class2 = self.create_class(number="2c")
        self.create_homework(self.subject, self.teacher, school_class2)

        qs = Homework.objects.visible_to_user(self.student)

        self.assertQuerysetEqual(qs, [self.homework])

    def test_visible_to_user_returns_empty_qs_if_user_is_neither_student_nor_teacher(
        self,
    ):
        parent = self.create_parent(child=self.student)

        qs = Homework.objects.visible_to_user(parent)

        self.assertQuerysetEqual(qs, Homework.objects.none())

    def test_with_realisations_count_selects_submitted_count_and_total_count(self):
        self.create_student(username="student2", school_class=self.school_class)
        self.create_realisation(self.homework, self.student)

        homework = Homework.objects.with_realisations_count().get()

        self.assertEqual(homework.submitted_count, 1)
        self.assertEqual(homework.total_count, 2)

    def test_with_realisations(self):
        student2 = self.create_student(
            username="student2", school_class=self.school_class
        )
        realisation = self.create_realisation(self.homework, self.student)
        self.create_realisation(self.homework, student2)

        homework = Homework.objects.with_realisations(self.student).get()

        self.assertEqual(homework.realisation, [realisation])

    def test_only_current_select_future_homeworks(self):
        completion_date = datetime.datetime.today() + datetime.timedelta(days=-100)
        self.create_homework(
            self.subject,
            self.teacher,
            self.school_class,
            completion_date=completion_date,
        )

        qs = Homework.objects.only_current()

        self.assertQuerysetEqual(qs, [self.homework])

    def test_only_current_select_homeworks_up_to_week_in_past(self):
        completion_date = datetime.datetime.today() + datetime.timedelta(days=-7)
        homework2 = self.create_homework(
            self.subject,
            self.teacher,
            self.school_class,
            completion_date=completion_date,
        )

        qs = Homework.objects.only_current()

        self.assertQuerysetEqual(qs, [self.homework, homework2], ordered=False)
