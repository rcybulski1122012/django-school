from functools import wraps

from django.core.exceptions import PermissionDenied

from django_school.apps.lessons.models import Lesson


class IsTeacherMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_teacher:
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)


def teacher_view(func):
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
