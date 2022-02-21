from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from django_school.apps.classes.models import Class
from django_school.apps.lessons.models import Lesson, Subject


def RolesRequiredMixin(*roles):
    class RolesRequiredMixin_:
        def dispatch(self, request, *args, **kwargs):
            if request.user.role not in roles and not request.user.is_superuser:
                raise PermissionDenied()

            return super().dispatch(request, *args, **kwargs)

    return RolesRequiredMixin_


def roles_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles and not request.user.is_superuser:
                raise PermissionDenied

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


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


def _is_htmx_request(request):
    return request.headers.get("Hx-Request", "") == "true"


class AjaxRequiredMixin:
    not_ajax_allowed_methods = ["POST"]

    def dispatch(self, *args, **kwargs):
        if self.request.method not in self.not_ajax_allowed_methods and not (
            self.request.is_ajax() or _is_htmx_request(self.request)
        ):
            raise PermissionDenied("Only ajax requests are allowed.")

        return super().dispatch(*args, **kwargs)


def ajax_required(not_ajax_allowed_methods=["POST"]):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method not in not_ajax_allowed_methods and not (
                request.is_ajax() or _is_htmx_request(request)
            ):
                raise PermissionDenied("Only ajax requests are allowed.")

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


class SubjectAndSchoolClassRelatedMixin:
    school_class = None
    subject = None

    def dispatch(self, request, *args, **kwargs):
        self.school_class = get_object_or_404(Class, slug=self.kwargs["class_slug"])
        self.subject = get_object_or_404(Subject, slug=self.kwargs["subject_slug"])

        if not does_the_teacher_teach_the_subject_to_the_class(
            self.request.user, self.subject, self.school_class
        ):
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "school_class": self.school_class,
                "subject": self.subject,
            }
        )

        return context
