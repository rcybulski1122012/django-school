from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from django_school.apps.users.context_processors import unseen_notes_count
from tests.utils import ClassesMixin, GradesMixin, LessonsMixin, UsersMixin


class UnseenNotesCountTestCase(
    UsersMixin, ClassesMixin, LessonsMixin, GradesMixin, TestCase
):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.parent = cls.create_parent(child=cls.student)
        cls.subject = cls.create_subject()
        cls.note = cls.create_note(cls.student, cls.teacher)

    def test_returns_empty_dict_if_user_is_not_authenticated_or_if_is_teacher(
        self,
    ):
        request = RequestFactory().get("/test")
        request.user = AnonymousUser()

        result = unseen_notes_count(request)
        self.assertEqual(result, {})

        request.user = self.teacher
        result = unseen_notes_count(request)
        self.assertEqual(result, {})

    def test_returns_unseen_grades_count(self):
        request = RequestFactory().get("/test")
        request.user = self.student

        result = unseen_notes_count(request)
        self.assertEqual(result, {"unseen_notes_count": 1})

        self.note.seen_by_student = True
        self.note.save()
        result = unseen_notes_count(request)
        self.assertEqual(result, {"unseen_notes_count": 0})

        request.user = self.parent
        result = unseen_notes_count(request)
        self.assertEqual(result, {"unseen_notes_count": 1})
