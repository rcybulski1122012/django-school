from functools import wraps

from django.core.exceptions import PermissionDenied

from django_school.apps.lessons.models import Lesson


class TeacherStatusRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_teacher:
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)


def teacher_status_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_teacher:
            raise PermissionDenied

        return func(request, *args, **kwargs)

    return wrapper


def does_the_teacher_teach_the_subject_to_the_class(teacher, subject, school_class):
    return Lesson.objects.filter(
        school_class=school_class,
        subject=subject,
        teacher=teacher,
    ).exists()


class GetObjectCacheMixin:
    object = None

    def get_object(self, queryset=None):
        if self.object is not None:
            return self.object

        self.object = super().get_object(queryset=queryset)
        return self.object


class AjaxRequiredMixin:
    not_ajax_allowed_methods = ["POST"]

    def dispatch(self, *args, **kwargs):
        if self.request.method not in self.not_ajax_allowed_methods and not (
            self.request.is_ajax() or self.is_htmx_request(self.request)
        ):
            raise PermissionDenied("Only ajax requests are allowed.")

        return super().dispatch(*args, **kwargs)

    def is_htmx_request(self, request):
        return request.headers.get("Hx-Request", "") == "true"
