from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from django_school.apps.grades.context_processors import unseen_grades_count
from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin


class UnseenGradesCountTestCase(
    UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(school_class=self.school_class)
        self.parent = self.create_parent(child=self.student)
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.category = self.create_grade_category(self.subject, self.school_class)
        self.grade = self.create_grade(
            self.category, self.subject, self.student, self.teacher
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
