from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views import View

from django_school.apps.common.utils import (
    AjaxRequiredMixin, GetObjectCacheMixin, TeacherStatusRequiredMixin,
    does_the_teacher_teach_the_subject_to_the_class, teacher_status_required)
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class TeacherStatusRequiredMixinTestCase(UsersMixin, TestCase):
    class DummyView(TeacherStatusRequiredMixin, View):
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


class TeacherStatusRequiredTestCase(UsersMixin, TestCase):
    @staticmethod
    @teacher_status_required
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


class GetObjectCacheMixinTestCase(TestCase):
    class DummyBaseView(View):
        get_object_calls_counter = 0

        def get_object(self, *args, **kwargs):
            self.__class__.get_object_calls_counter += 1
            return "Object"

        def get(self, *args, **kwargs):
            return HttpResponse("OK")

    class DummyView(GetObjectCacheMixin, DummyBaseView):
        def get(self, *args, **kwargs):
            for _ in range(5):
                self.get_object()

    def test_caches_object(self):
        request = RequestFactory().get("/test")
        view = self.DummyView.as_view()

        view(request)

        self.assertEqual(self.DummyView.get_object_calls_counter, 1)


class AjaxRequiredMixinTestCase(TestCase):
    class DummyView(AjaxRequiredMixin, View):
        def get(self, *args, **kwargs):
            return HttpResponse("OK")

        def post(self, *args, **kwargs):
            return HttpResponse("OK")

    def test_raises_PermissionDenied_if_request_not_ajax_and_method_not_allowed(self):
        request = RequestFactory().get("/test")
        view = self.DummyView.as_view()

        with self.assertRaises(PermissionDenied):
            view(request)

    def test_does_not_raise_if_request_is_ajax(self):
        request = RequestFactory().get("/test", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        view = self.DummyView.as_view()

        view(request)

    def test_does_not_raise_if_request_method_in_not_ajax_allowed_methods(self):
        request = RequestFactory().post("/test")
        view = self.DummyView.as_view()

        view(request)

    def test_does_not_raise_if_request_is_htmx_request(self):
        request = RequestFactory().get("/test", HTTP_HX_REQUEST="true")
        print(request.headers)
        view = self.DummyView.as_view()

        view(request)
