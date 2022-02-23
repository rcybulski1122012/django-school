from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from django_school.apps.grades.context_processors import unseen_grades_count
from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin


class UnseenGradesCountTestCase(
    UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase
):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.parent = cls.create_parent(child=cls.student)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.category = cls.create_grade_category(cls.subject, cls.school_class)
        cls.grade = cls.create_grade(
            cls.category, cls.subject, cls.student, cls.teacher
        )

    def test_returns_empty_dict_if_the_user_is_not_authenticated_or_if_is_a_teacher(
        self,
    ):
        request = RequestFactory().get("/test")
        request.user = AnonymousUser()

        result = unseen_grades_count(request)
        self.assertEqual(result, {})

        request.user = self.teacher
        self.assertEqual(result, {})

    def test_returns_unseen_grades_count(self):
        request = RequestFactory().get("/test")
        request.user = self.student

        result = unseen_grades_count(request)
        self.assertEqual(result, {"unseen_grades_count": 1})

        self.grade.seen_by_student = True
        self.grade.save()
        result = unseen_grades_count(request)
        self.assertEqual(result, {"unseen_grades_count": 0})

        request.user = self.parent
        result = unseen_grades_count(request)
        self.assertEqual(result, {"unseen_grades_count": 1})
