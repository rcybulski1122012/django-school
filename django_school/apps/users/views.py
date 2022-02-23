from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import DetailView

from django_school.apps.common.utils import RolesRequiredMixin
from django_school.apps.users.models import ROLES

User = get_user_model()


class StudentDetailView(
    LoginRequiredMixin, RolesRequiredMixin(ROLES.TEACHER), DetailView
):
    model = User
    slug_url_kwarg = "student_slug"
    template_name = "users/student_detail.html"
    context_object_name = "user"

    def dispatch(self, request, *args, **kwargs):
        if self.is_requested_user_a_teacher():
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def is_requested_user_a_teacher(self):
        return User.objects.filter(
            slug=self.kwargs[self.slug_url_kwarg], role=ROLES.TEACHER
        ).exists()

    def get_queryset(self):
        return super().get_queryset().select_related("address", "school_class__tutor")


class PasswordChangeWithMessageView(SuccessMessageMixin, PasswordChangeView):
    success_url = reverse_lazy("index")
    success_message = "The password has been changed successfully."
