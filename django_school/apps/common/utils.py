from functools import wraps

from django.core.exceptions import PermissionDenied


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
