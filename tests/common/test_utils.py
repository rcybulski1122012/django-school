from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views import View

from django_school.apps.common.utils import (
    IsTeacherMixin, does_the_teacher_teach_the_subject_to_the_class,
    teacher_view)
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class TestIsTeacherMixin(UsersMixin, TestCase):
    class DummyView(IsTeacherMixin, View):
        def get(self, *args, **kwargs):
            return HttpResponse("OK")

    def test_dispatch_raises_404_if_user_is_not_a_teacher(self):
        teacher = self.create_teacher()
        student = self.create_student()
        request = RequestFactory().get("/test")
        view = self.DummyView()

        request.user = teacher
        view.dispatch(request)

        request.user = student
        with self.assertRaises(PermissionDenied):
            view.dispatch(request)


class TeacherViewDecoratorTestCase(UsersMixin, TestCase):
    @staticmethod
    @teacher_view
    def dummy_view(request):
        return HttpResponse("OK")

    def test_decorated_view_raises_404_if_user_is_not_a_teacher(self):
        teacher = self.create_teacher()
        student = self.create_student()
        request = RequestFactory().get("/test")

        request.user = teacher
        self.dummy_view(request)

        request.user = student
        with self.assertRaises(PermissionDenied):
            self.dummy_view(request)


from django.test import TestCase


class DoesTheTeacherTeachTheSubjectToTheClassTestCase(
    UsersMixin, ClassesMixin, LessonsMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.subject = self.create_subject()

    def test_if_teacher_teaches(self):
        self.create_lesson(self.subject, self.teacher, self.school_class)

        result = does_the_teacher_teach_the_subject_to_the_class(
            self.teacher, self.subject, self.school_class
        )

        self.assertTrue(result)

    def test_if_teacher_does_not_teach(self):
        result = does_the_teacher_teach_the_subject_to_the_class(
            self.teacher, self.subject, self.school_class
        )

        self.assertFalse(result)
