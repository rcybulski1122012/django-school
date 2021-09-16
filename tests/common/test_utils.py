from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views import View

from django_school.apps.common.utils import IsTeacherMixin, teacher_view
from tests.utils import UsersMixin


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
